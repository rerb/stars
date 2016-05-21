from datetime import datetime, date
from itertools import chain

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView, CreateView
from django.db.models import Max, Q
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
from extra_views import UpdateWithInlinesView

from stars.apps.helpers.forms.forms import Confirm
from stars.apps.institutions.models import FULL_ACCESS, MigrationHistory
from stars.apps.notifications.models import EmailTemplate
from stars.apps.submissions.models import (Boundary,
                                           CreditUserSubmission,
                                           RATING_VALID_PERIOD,
                                           ResponsibleParty,
                                           SUBMISSION_STATUSES,
                                           SubcategorySubmission,
                                           SubmissionSet)
from stars.apps.submissions.tasks import (
    rollover_submission,
    send_email_with_certificate_attachment,
    take_snapshot_task)
from stars.apps.tool.mixins import (UserCanEditSubmissionMixin,
                                    UserCanEditSubmissionOrIsAdminMixin,
                                    SubmissionToolMixin)
from stars.apps.tool.my_submission import credit_history
from stars.apps.tool.my_submission.forms import (
    ApproveSubmissionForm,
    ContactsForm,
    CreditReviewForm,
    CreditReviewNotationInlineFormSet,
    CreditUserSubmissionForm,
    CreditUserSubmissionNotesForm,
    LetterForm,
    StatusForm,
    ResponsiblePartyForm,
    SubcategorySubmissionForm)
from stars.apps.tool.my_submission.forms import NewBoundaryForm


class SubmissionSummaryView(UserCanEditSubmissionMixin,
                            TemplateView):
    """
        Though called a summary view, this actually throws up a template
        through which a submission can be edited.
    """
    template_name = 'tool/submissions/summary.html'

    def get_context_data(self, **kwargs):
        context = super(SubmissionSummaryView, self).get_context_data(**kwargs)

        submissionset = self.get_submissionset()

        context['category_submission_list'] = (
            submissionset.categorysubmission_set.all().select_related())

        context['submission_under_review'] = (
            submissionset.status == SUBMISSION_STATUSES["REVIEW"])

        # Show the migration message if there was a recent migration
        # and the score is zero, unless the submission is under review
        context['show_migration_warning'] = False
        i = self.get_institution()
        migration_list = MigrationHistory.objects.filter(institution=i)
        if migration_list:
            max_date = migration_list.aggregate(Max('date'))['date__max']
            time_delta = datetime.now() - max_date
            if (time_delta.days < 30 and
                not context['submission_under_review']):

                context['show_migration_warning'] = True
                context['last_migration_date'] = max_date

        context['outline'] = self.get_submissionset_nav()

        return context


class EditBoundaryView(UserCanEditSubmissionMixin, UpdateView):
    """
        A basic view to edit the boundary
    """
    template_name = "tool/submissions/boundary.html"
    form_class = NewBoundaryForm
    model = Boundary

    def form_valid(self, form):
        if not self.object:
            self.object = form.save(commit=False)
            self.object.submissionset = self.get_submissionset()
        return super(EditBoundaryView, self).form_valid(form)

    def get_object(self):
        try:
            return self.get_submissionset().boundary
        except Boundary.DoesNotExist:
            return None


class SubmitRedirectMixin():

    def redirect_to_boundary(self):
        messages.error(self.request,
                      ("You must complete your Institutional Boundary"
                       " before submitting for a rating."))
        return HttpResponseRedirect(reverse('boundary-edit',
                                            kwargs={
                                                'institution_slug':
                                                self.get_institution().slug,
                                                'submissionset':
                                                self.get_submissionset().id
                                                }))

    def redirect_to_my_submission(self):
        messages.error(self.request,
                       ("One or more required credits are not complete."))
        return HttpResponseRedirect(reverse(
            'submission-summary',
            kwargs={'institution_slug': self.get_institution().slug,
                    'submissionset': self.get_submissionset().id}))


class SaveSnapshot(SubmitRedirectMixin, SubmissionToolMixin, TemplateView):
    """
        First step in the form for submission
    """
    template_name = "tool/submissions/submit_snapshot.html"

    def update_logical_rules(self):
        self.add_logical_rule(
            {'name': 'user_can_submit_snapshot',
             'param_callbacks': [('user', 'get_request_user'),
                                 ('submission', 'get_submissionset')],
             'message': ("Sorry, you do not have privileges "
                         "to submit a snapshot of this submission.")})
        self.add_logical_rule({
            'name': 'submission_is_not_missing_required_boundary',
            'param_callbacks': [('submission',
                                 'get_submissionset')],
            'response_callback': 'redirect_to_boundary'
        })
        super(SaveSnapshot, self).update_logical_rules()

    def get_context_data(self, **kwargs):
        _context = super(SaveSnapshot, self).get_context_data(**kwargs)
        _context['task'] = take_snapshot_task.delay(self.get_submissionset(),
                                                    self.request.user)
        return _context

    def post(self, request, *args, **kwargs):
        return self.get(request, args, kwargs)


SUBMISSION_STEPS = [
    {
        'form': StatusForm,
        'template': 'status',
        'instance_callback': 'get_submissionset'
    },
    {
        'form': LetterForm,
        'template': 'letter',
        'instance_callback': 'get_submissionset'
    },
    {
        'form': ContactsForm,
        'template': 'contacts',
        'instance_callback': 'get_institution'
    },
    {
        'form': Confirm,
        'template': 'finalize',
        'instance_callback': None
    },
]


class SubmitForRatingWizard(SubmitRedirectMixin,
                            SubmissionToolMixin,
                            SessionWizardView):
    """
        A wizard that runs a user through the forms
        required to submit for a rating
    """
    file_storage = FileSystemStorage(location='/tmp/stars_wizard_files/')

    def update_logical_rules(self):
        super(SubmitForRatingWizard, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_can_submit_report',
            'param_callbacks': [
                ('user', 'get_request_user'),
                ('submission', 'get_submissionset')
            ],
            'message': "Sorry, you do not have privileges "
            "to submit a report."
        })
        self.add_logical_rule({
            'name': 'submission_is_not_missing_required_boundary',
            'param_callbacks': [('submission',
                                 'get_submissionset')],
            'response_callback': 'redirect_to_boundary'
        })
        self.add_logical_rule({
            'name': 'required_credits_are_complete',
            'param_callbacks': [('submission',
                                 'get_submissionset')],
            'response_callback': 'redirect_to_my_submission'
        })

    def get_template_names(self):
        return ("tool/submissions/submit_wizard_%s.html" %
                SUBMISSION_STEPS[int(self.steps.current)]['template'])

    def get_form_instance(self, step):
        if SUBMISSION_STEPS[int(step)]['instance_callback']:
            return getattr(self,
                           SUBMISSION_STEPS[int(step)]['instance_callback'])()
        return None

    def get_context_data(self, form, **kwargs):
        _context = super(SubmitForRatingWizard, self).get_context_data(
            form=form, **kwargs)

        if self.steps.current == '0':
            qs = CreditUserSubmission.objects.all()
            qs = qs.filter(subcategory_submission__category_submission__submissionset=self.get_submissionset())
            qs = qs.filter(Q(submission_status='p') |
                           Q(submission_status='ns'))
            qs = qs.order_by('subcategory_submission__category_submission__category__ordinal','credit__number')
            _context['credit_list'] = qs
            _context['reporter_rating'] = self.get_submissionset().creditset.rating_set.get(name='Reporter')

        return _context

    def done(self, form_list, **kwargs):
        for form in form_list:
            if hasattr(form, 'save'):  # When might this be False?
                form.save()

        submissionset = self.get_submissionset(use_cache=False)

        self.setup_submissionset_for_review(submissionset=submissionset)

        # My Submission gets cached, and in the cache it still looks
        # like it's not under review, so flush that mother here.
        submissionset.invalidate_cache()

        redirect_url = reverse('submit-success',
                               kwargs={'institution_slug':
                                       self.get_institution().slug,
                                       'submissionset':
                                       submissionset.id})
        return HttpResponseRedirect(redirect_url)

    def setup_submissionset_for_review(self, submissionset):

        # Save the submission
        submissionset.date_submitted = date.today()
        submissionset.rating = submissionset.get_STARS_rating()
        submissionset.status = SUBMISSION_STATUSES["REVIEW"]
        submissionset.submitting_user = self.request.user
        submissionset.save()

        # Send mail to STARS Liaison.
        if not submissionset.reporter_status:
            email_template = EmailTemplate.objects.get(
                slug="submission_for_rating")
        else:
            email_template = EmailTemplate.objects.get(
                slug="submission_as_reporter")

        stars_liaison_email = submissionset.institution.contact_email
        email_template.send_email([stars_liaison_email],
                                  {'submissionset': submissionset})


class SubmitSuccessView(SubmissionToolMixin, TemplateView):
    """
        Return a congratulations page when a submission is made.
    """
    template_name = 'tool/submissions/submit_success.html'

    def get(self, *args, **kwargs):
        return super(SubmitSuccessView, self).get(*args, **kwargs)


class ApproveSubmissionView(SubmissionToolMixin, UpdateView):

    model = SubmissionSet
    template_name = 'tool/submissions/approve_submission_confirmation.html'
    form_class = ApproveSubmissionForm

    def get_object(self, *args, **kwargs):
        return self.get_submissionset()

    def form_valid(self, form):

        submissionset = self.get_submissionset(use_cache=False)

        # Update the SubmissionSet.
        submissionset.rating = submissionset.get_STARS_rating()
        submissionset.status = SUBMISSION_STATUSES["RATED"]
        submissionset.submitting_user = self.request.user
        submissionset.save()

        # Send email to STARS Liaison, Executive Contact,
        # and institution President.
        institution = submissionset.institution

        recipients = [email for email in (institution.contact_email,
                                          institution.executive_contact_email,
                                          institution.president_email)
                      if email]

        if not submissionset.reporter_status:
            email_template = EmailTemplate.objects.get(
                slug="published_rating")
            send_email_with_certificate_attachment(
                submissionset=submissionset,
                email_template=email_template,
                email_context={'submissionset': submissionset},
                recipients=recipients)
        else:
            email_template = EmailTemplate.objects.get(
                slug="published_reporter")
            email_template.send_email(recipients,
                                      {'submissionset': submissionset})

        # Update institution subscription data.
        if institution.current_subscription:
            institution.current_subscription.ratings_used += 1
            institution.current_subscription.save()

        institution.current_rating = submissionset.rating
        institution.rated_submission = submissionset
        institution.rating_expires = date.today() + RATING_VALID_PERIOD
        institution.save()

        # Update their current submission.
        rollover_submission.delay(submissionset)

        return super(ApproveSubmissionView, self).form_valid(form)

    def get_success_url(self):
        url = reverse(
            'tool-summary',
            kwargs={'institution_slug': self.get_institution().slug})
        return url


class SubcategorySubmissionDetailView(UserCanEditSubmissionOrIsAdminMixin,
                                      UpdateView):

    model = SubcategorySubmission
    template_name = 'tool/submissions/subcategory.html'
    form_class = SubcategorySubmissionForm

    def get_object(self, queryset=None):
        obj = self.get_subcategorysubmission()
        return obj

    def get_context_data(self, **kwargs):
        context = super(SubcategorySubmissionDetailView,
                        self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
        context['outline'] = self.get_submissionset_nav()
        return context

    def get_success_url(self):
        url = self.request.POST.get('next', False)
        if not url:
            url = reverse(
                'submission-summary',
                kwargs={'institution_slug': self.get_institution().slug,
                        'submissionset': self.get_submissionset().id})
        return url

    def form_valid(self, form):
        if form.has_changed():
            submissionset = self.get_object().get_submissionset()
            submissionset.invalidate_cache()
        return super(SubcategorySubmissionDetailView, self).form_valid(form)


class CreditSubmissionDetailView(UserCanEditSubmissionMixin):

    model = CreditUserSubmission

    def get_object(self, queryset=None):
        return self.get_creditsubmission()

    def get_context_data(self, *args, **kwargs):
        context = super(CreditSubmissionDetailView, self).get_context_data(
            *args, **kwargs)

        context['outline'] = self.get_submissionset_nav()
        context['credit_submission_locked'] = (
            self.get_creditsubmission().is_locked())

        return context


class CreditSubmissionReportingFieldsView(CreditSubmissionDetailView,
                                          UpdateView):

    template_name = "tool/submissions/credit_reporting_fields.html"
    form_class = CreditUserSubmissionForm

    def get_success_url(self):
        return self.get_creditsubmission().get_submit_url()

    def form_invalid(self, form):
        messages.error(self.request,
                       "Credit data has <b>NOT BEEN SAVED</b>! Please correct "
                       "the errors below.")
        return super(CreditSubmissionReportingFieldsView,
                     self).form_invalid(form)

    def form_valid(self, form):
        if form.has_warnings():
            # @todo: do this on GET too
            messages.info(self.request,
                          "Some data values are not within the expected range "
                          "- see notes below.")
        return super(CreditSubmissionReportingFieldsView,
                     self).form_valid(form)


class CreditSubmissionDocumentationView(CreditSubmissionDetailView,
                                        TemplateView):

    template_name = "tool/submissions/credit_info.html"

    def get_template_names(self):
        if self.request.GET.get('popup', False):
            return ["tool/submissions/credit_info_popup.html"]
        return super(CreditSubmissionDocumentationView,
                     self).get_template_names()


class CreditSubmissionNotesView(CreditSubmissionDetailView,
                                UpdateView):

    template_name = "tool/submissions/credit_notes.html"
    form_class = CreditUserSubmissionNotesForm


class CreditSubmissionHistoryView(CreditSubmissionDetailView,
                                  TemplateView):
    """
        Displays a list of submission history for a credit
        (based on DocumentationFieldSubmissions).
    """
    tab_content_title = 'history'
    template_name = "tool/submissions/credit_history.html"

    def get_history(self):
        history = credit_history.get_credit_submission_history(
            credit_submission=self.get_creditsubmission())
        return history

    def get_context_data(self, *args, **kwargs):
        context = super(CreditSubmissionHistoryView,
                        self).get_context_data(
            *args, **kwargs)
        history = self.get_history()
        context['history'] = history
        if history:
            all_documentation_field_submissions = reduce(chain,
                                                         history.values())
        else:
            all_documentation_field_submissions = []
        context['exportable_submissionsets'] = set(
            [
                history_.doc_field_sub.get_submissionset() for history_
                in all_documentation_field_submissions
                if getattr(history_.doc_field_sub,
                           'get_submissionset',
                           False)
            ]
        )
        context['institution_has_full_access'] = (
            context['institution'].access_level == FULL_ACCESS)

        return context


class CreditSubmissionResourcesView(CreditSubmissionDetailView,
                                    TemplateView):

    template_name = "tool/submissions/credit_resources.html"


class CreditSubmissionReviewView(CreditSubmissionDetailView,
                                 UpdateWithInlinesView):

    form_class = CreditReviewForm
    inlines = [CreditReviewNotationInlineFormSet]

    def get_template_names(self):
        if self.request.GET.get('popup', False):
            return ["tool/submissions/credit_review_popup.html"]
        else:
            return ["tool/submissions/credit_review.html"]
        return super(CreditSubmissionReviewView, self).get_template_names()


class AddResponsiblePartyView(UserCanEditSubmissionMixin, CreateView):

    template_name = "tool/submissions/responsible_party.html"
    form_class = ResponsiblePartyForm
    model = ResponsibleParty

    def get_form_kwargs(self):
        obj = ResponsibleParty(institution=self.get_institution())
        kwargs = super(AddResponsiblePartyView, self).get_form_kwargs()
        kwargs.update({'instance': obj})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return self.response_class(
            request=self.request,
            template=["tool/submissions/responsible_party_redirect.html"],
            context={'rp': self.object}
        )
