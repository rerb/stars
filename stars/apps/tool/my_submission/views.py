from datetime import datetime, date
from itertools import chain
import os

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.db.models import Max, Q
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage

from stars.apps.helpers.forms.forms import Confirm
from stars.apps.institutions.models import FULL_ACCESS, MigrationHistory
from stars.apps.notifications.models import EmailTemplate
from stars.apps.submissions.models import (Boundary,
                                           CreditUserSubmission,
                                           RATED_SUBMISSION_STATUS,
                                           RATING_VALID_PERIOD,
                                           ResponsibleParty,
                                           SubcategorySubmission)
from stars.apps.submissions.tasks import (send_certificate_pdf,
                                          rollover_submission)
from stars.apps.tool.mixins import (UserCanEditSubmissionMixin,
                                    SubmissionToolMixin,)
from stars.apps.tool.my_submission import credit_history
from stars.apps.tool.my_submission.forms import (CreditUserSubmissionForm,
                                                 CreditUserSubmissionNotesForm,
                                                 ExecContactForm,
                                                 LetterForm,
                                                 StatusForm,
                                                 ResponsiblePartyForm,
                                                 SubcategorySubmissionForm)
from stars.apps.tool.my_submission.forms import NewBoundaryForm


class SubmissionSummaryView(UserCanEditSubmissionMixin, TemplateView):
    """
        Though called a summary view, this actually throws up a template
        through which a submission can be edited.
    """
    template_name = 'tool/submissions/summary.html'

    def get_context_data(self, **kwargs):
        context = super(SubmissionSummaryView, self).get_context_data(**kwargs)

        context['category_submission_list'] = self.get_submissionset(
            ).categorysubmission_set.all().select_related()

        # Show the migration message if there was a recent migration
        # and the score is zero
        context['show_migration_warning'] = False
        i = self.get_institution()
        migration_list = MigrationHistory.objects.filter(institution=i)
        if migration_list:
            max_date = migration_list.aggregate(Max('date'))['date__max']
            time_delta = datetime.now() - max_date
            if time_delta.days < 30:
                context['show_migration_warning'] = True
                context['last_migration_date'] = max_date
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


class SaveSnapshot(SubmissionToolMixin, FormView):
    """
        First step in the form for submission
    """
    form_class = Confirm
    template_name = "tool/submissions/submit_snapshot.html"

    def update_logical_rules(self):
        self.add_logical_rule({
                               'name': 'user_can_submit_snapshot',
                               'param_callbacks': [
                                    ('user', 'get_request_user'),
                                    ('submission', 'get_submissionset')
                                                   ],
                               'message': "Sorry, you do not have privileges "
                                   "to submit a snapshot of this submission."
                               })
        super(SaveSnapshot, self).update_logical_rules()

    def get_success_url(self):
        return reverse(
                       'share-data',
                       kwargs={'institution_slug': self.get_institution().slug}
                       )

    def get_context_data(self, **kwargs):
        _context = super(SaveSnapshot, self).get_context_data(**kwargs)
        _context['active_submission'] = self.get_institution().current_submission
        return _context

    def form_valid(self, form):
        """
            When the form validates, create a finalized submission
        """
        ss = self.get_institution().current_submission
        ss.take_snapshot(user=self.request.user)
        return super(SaveSnapshot, self).form_valid(form)

    def render_to_response(self, context, **response_kwargs):

        try:
            _ = context['active_submission'].boundary
        except Boundary.DoesNotExist:
            messages.info(self.request,
                          "You must complete your Boundary before submitting.")
            return HttpResponseRedirect(
                reverse('boundary-edit',
                    kwargs={'institution_slug': self.get_institution().slug,
                            'submissionset': self.get_submissionset().id}))

        return super(SaveSnapshot, self).render_to_response(
            context, **response_kwargs)


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
                        'form': ExecContactForm,
                        'template': 'exec',
                        'instance_callback': 'get_institution'
                    },
                    {
                        'form': Confirm,
                        'template': 'finalize',
                        'instance_callback': None
                    },
]


class SubmitForRatingWizard(SubmissionToolMixin, SessionWizardView):
    """
        A wizard that runs a user through the forms
        required to submit for a rating
    """
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT,
                                                           'temp'))

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

    def get_template_names(self):
        return ("tool/submissions/submit_wizard_%s.html" %
                SUBMISSION_STEPS[int(self.steps.current)]['template'])

    def get_form_instance(self, step):
        if SUBMISSION_STEPS[int(step)]['instance_callback']:
            return getattr(self,
                           SUBMISSION_STEPS[int(step)]['instance_callback'])()
        return None

    def get_context_data(self, form, **kwargs):
        _context = super(SubmitForRatingWizard, self).get_context_data(form=form, **kwargs)

        if self.steps.current == '0':

            qs = CreditUserSubmission.objects.all()
            qs = qs.filter(subcategory_submission__category_submission__submissionset=self.get_submissionset())
            qs = qs.filter(Q(submission_status='p') |
                           Q(submission_status='ns'))
            qs = qs.order_by('subcategory_submission__category_submission__category__ordinal','credit__number')
            _context['credit_list'] = qs
            _context['reporter_rating'] = self.get_submissionset().creditset.rating_set.get(name='Reporter')
        return _context

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

    def done(self, form_list, **kwargs):
        for form in form_list:
            if hasattr(form, 'save'):
                form.save()

        self.finalize_rating()

        redirect_url = reverse('submit-success',
                                kwargs={'institution_slug':
                                        self.get_institution().slug,
                                        'submissionset':
                                        self.get_submissionset().id})
        return HttpResponseRedirect(redirect_url)

    def finalize_rating(self):

        ss = self.get_submissionset(use_cache=False)
        institution = ss.institution

        # Save the submission
        ss.date_submitted = date.today()
        ss.rating = ss.get_STARS_rating()
        ss.status = RATED_SUBMISSION_STATUS
        ss.submitting_user = self.request.user
        ss.save()

        # Send email to submitting institution
        et = EmailTemplate.objects.get(slug="submission_for_rating")
        et.send_email([institution.contact_email],
                      {'submissionset': ss})

        if institution.current_subscription:
            institution.current_subscription.ratings_used += 1
            institution.current_subscription.save()

        institution.current_rating = ss.rating
        institution.rated_submission = ss
        institution.rating_expires = date.today() + RATING_VALID_PERIOD
        institution.save()

        # update their current submission
        rollover_submission.delay(ss)

        # Send certificate to staff
        send_certificate_pdf.delay(ss)


class RatingCongratulationsView(SubmissionToolMixin, TemplateView):
    """
        Return a congratulations page on the most recent rating
    """
    template_name = 'tool/submissions/submit_success.html'

    def get(self, *args, **kwargs):
        return super(RatingCongratulationsView, self).get(*args, **kwargs)


class SubcagegorySubmissionDetailView(UserCanEditSubmissionMixin, UpdateView):

    model = SubcategorySubmission
    template_name = 'tool/submissions/subcategory.html'
    form_class = SubcategorySubmissionForm

    def get_object(self, queryset=None):
        obj = self.get_subcategorysubmission()
        return obj

    def get_success_url(self):
        return reverse('submission-summary',
                    kwargs={'institution_slug': self.get_institution().slug,
                            'submissionset': self.get_submissionset().id})


class CreditSubmissionDetailView(UserCanEditSubmissionMixin, UpdateView):

    model = CreditUserSubmission
    template_name = "tool/submissions/credit_reporting_fields.html"
    form_class = CreditUserSubmissionForm

    def get_object(self, queryset=None):
        return self.get_creditsubmission()

    def get_success_url(self):
        return self.get_creditsubmission().get_submit_url()

    def form_invalid(self, form):
        messages.error(self.request,
                      "Credit data has <b>NOT BEEN SAVED</b>! Please correct "
                      "the errors below.")
        return super(CreditSubmissionDetailView, self).form_invalid(form)

    def form_valid(self, form):
        if form.has_warnings():
            # @todo: do this on GET too
            messages.info(self.request,
                      "Some data values are not within the expected range "
                      "- see notes below.")
        return super(CreditSubmissionDetailView, self).form_valid(form)


class CreditDocumentationView(UserCanEditSubmissionMixin, TemplateView):

    template_name = "tool/submissions/credit_info.html"

    def get_template_names(self):
        if self.request.GET.get('popup', False):
            return ["tool/submissions/credit_info_popup.html"]
        return super(CreditDocumentationView, self).get_template_names()


class CreditNotesView(UserCanEditSubmissionMixin, UpdateView):

    template_name = "tool/submissions/credit_notes.html"
    form_class = CreditUserSubmissionNotesForm
    model = CreditUserSubmission

    def get_object(self):
        return self.get_creditsubmission()


class CreditHistoryView(UserCanEditSubmissionMixin,
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
        context = super(CreditHistoryView, self).get_context_data(
            *args, **kwargs)
        history = self.get_history()
        context['history'] = history
        if history:
            all_documentation_field_submissions = reduce(chain,
                                                         history.values())
        else:
            all_documentation_field_submissions = []
        context['exportable_submissionsets'] = set(
            [ history_.doc_field_sub.get_submissionset() for history_
              in all_documentation_field_submissions ])
        context['institution_has_full_access'] = (
            context['institution'].access_level == FULL_ACCESS)
                
        return context


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
