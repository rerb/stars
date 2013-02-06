from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView

from stars.apps.accounts.decorators import user_has_tool
from stars.apps.accounts.mixins import SubmissionMixin
from stars.apps.accounts.utils import respond
from stars.apps.credits.models import Category, Credit, Subcategory
from stars.apps.helpers.forms.form_helpers import (basic_save_form,
                                                   basic_save_new_form)
from stars.apps.helpers.forms.forms import Confirm
from stars.apps.helpers.forms.views import FormActionView, MultiFormView
from stars.apps.institutions.views import InstitutionStructureMixin
from stars.apps.institutions.models import Institution
from stars.apps.notifications.models import EmailTemplate
from stars.apps.submissions.models import (Boundary,
                                           CategorySubmission,
                                           CreditUserSubmission,
                                           ResponsibleParty,
                                           SubcategorySubmission,
                                           SubmissionSet,
                                           UploadSubmission)
from stars.apps.submissions.rules import (user_can_submit_for_rating,
                                          user_can_edit_submission,
                                          user_can_submit_snapshot)
from stars.apps.submissions.tasks import (send_certificate_pdf,
                                          rollover_submission)
from stars.apps.submissions.views import SubmissionStructureMixin
from stars.apps.tool.mixins import UserCanEditSubmissionMixin
from stars.apps.tool.my_submission.forms import (CreditUserSubmissionForm,
                                                 CreditUserSubmissionNotesForm,
                                                 ExecContactForm,
                                                 LetterForm,
                                                 LetterStatusForm,
                                                 ResponsiblePartyForm,
                                                 SubcategorySubmissionForm)
from stars.apps.tool.my_submission.forms import NewBoundaryForm

def _get_active_submission(request, current_inst):

    active_submission = (current_inst.get_active_submission()
                         if current_inst
                         else None)

    if not user_can_edit_submission(request.user, active_submission):
        messages.error(request,
                       "Sorry, but you do not have access to edit "
                       "this submission")
        raise PermissionDenied()

    if active_submission.is_locked:
        messages.error(request,
                       "This submission is locked. It may be in the "
                       "process of being migrated. Please try again.")

    return active_submission


class SubmissionSummaryView(UserCanEditSubmissionMixin, TemplateView):
    """
        Though called a summary view, this actually throws up a template
        through which a submission can be edited.
    """
    template_name = 'tool/submissions/summary.html'

    def update_logical_rules(self):
        super(SubmissionSummaryView, self).update_logical_rules()
        self.add_logical_rule({ 'name': 'user_has_view_access',
                                'param_callbacks': [
                                    ('user', 'get_request_user'),
                                    ('institution', 'get_institution')] })

    def get_context_data(self, **kwargs):
        context = super(SubmissionSummaryView, self).get_context_data(**kwargs)
        context['category_submission_list'] = self.get_submissionset(
            ).categorysubmission_set.all().select_related()
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


class SaveSnapshot(InstitutionStructureMixin,
                   SubmissionStructureMixin,
                   FormView):
    """
        First step in the form for submission

        @todo: get current submission mixin
        @todo: add permission mixin
    """
    form_class = Confirm
    template_name = "tool/submissions/submit_snapshot.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SaveSnapshot, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse(
            'share-data',
            kwargs={'institution_slug': self.get_institution().slug})

    def get_context_data(self, **kwargs):
        _context = super(SaveSnapshot, self).get_context_data(**kwargs)
        _context['active_submission'] =  _get_active_submission(
            self.request, self.get_institution())
        return _context

    def form_valid(self, form):
        """
            When the form validates, create a finalized submission
        """
        ss = _get_active_submission(self.request,
                                    self.get_institution())
        ss.take_snapshot(user=self.request.user)
        return super(SaveSnapshot, self).form_valid(form)

    def render_to_response(self, context, **response_kwargs):

        if not user_can_submit_snapshot(self.request.user,
                                        context['active_submission']):
            raise PermissionDenied("Sorry, you do not have privileges "
                                   "to submit a snapshot.")

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


class SubmitForRatingMixin(InstitutionStructureMixin,
                           SubmissionStructureMixin,
                           SubmissionMixin):
    """
        Extends ``FormActionView`` to provide the class with the model instance
    """
    def __init__(self, *args, **kwargs):
        super(SubmitForRatingMixin, self).__init__(*args, **kwargs)

    def get_extra_context(self, request, *args, **kwargs):
        """ Extend this method to add any additional items to the context """
        # self.get_institution() depends on self.kwargs, which
        # isn't assigned when this method is called -- it gets
        # assigned in django.views.generic.BaseView.dispatch,
        # but that hasn't happened yet.  Since we want to pop
        # the institution into self.instance_name, we're popping
        # **kwargs onto self here.
        try:
            self.kwargs.update(kwargs)
        except AttributeError:
            self.kwargs = kwargs
        return {
            self.instance_name: _get_active_submission(
                request,
                self.get_institution()),
            'institution': self.get_institution(),
            'submissionset': self.get_submissionset()
            }

    def get_instance(self, request, context, *args, **kwargs):
        """
            Get's the active submission from the request
            and confirms that the user can submit for a rating
        """
        if context.has_key(self.instance_name):
            if not user_can_submit_for_rating(request.user,
                                              context[self.instance_name]):
                raise PermissionDenied(
                    "Sorry, you cannot submit for a rating either because "
                    "you are not an administrator or you are not a STARS "
                    "participant.")
            return context[self.instance_name]
        return None


class ConfirmClassView(SubmitForRatingMixin, TemplateView):
    """
        The first step in the final submission process
    """

    template_name = 'tool/submissions/submit_confirm.html'
    instance_name = "active_submission"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ConfirmClassView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        _context = self.get_extra_context(self.request, None, None)
        # Find all Credits listed as "In Progress"
        credit_list = []
        for cat in _context[self.instance_name].categorysubmission_set.all():
                for sub in cat.subcategorysubmission_set.all():
                    for c in sub.creditusersubmission_set.all():
                        if (c.submission_status == 'p' or
                            c.submission_status == 'ns'):
                            credit_list.append(c)
        _context.update({'credit_list': credit_list,})
        return _context

    def render_to_response(self, context, **response_kwargs):

        if not user_can_submit_for_rating(self.request.user,
                                          context[self.instance_name]):
            raise PermissionDenied("Sorry, you do not have privileges to "
                                   "submit for a rating.")

        try:
            _ = context[self.instance_name].boundary
        except Boundary.DoesNotExist:
            messages.info(self.request,
                          "You must complete your Boundary before submitting.")
            return HttpResponseRedirect(
                reverse('boundary-edit',
                        kwargs={'institution_slug': self.get_institution().slug,
                                'submissionset': self.get_submissionset().id}))

        if len(context['credit_list']) == 0:
            return HttpResponseRedirect(
                reverse('submit_letter',
                        kwargs={'institution_slug': self.get_institution().slug,
                                'submissionset': self.get_submissionset().id}))

        return super(ConfirmClassView, self).render_to_response(
            context, **response_kwargs)


class LetterClassView(SubmitForRatingMixin, MultiFormView):
    """
        Extends the Form class-based view from apps.helpers

    """
    form_class_list = [{ 'form_name': 'exec_contact_form',
                         'form_class': ExecContactForm,
                         'instance_name': 'institution',
                         'has_upload': False, }]
    instance_name = 'active_submission'

    def __init__(self, *args, **kwargs):
        super(LetterClassView, self).__init__(*args, **kwargs)
        self.init_context = {}

    def get_extra_context(self, request, context, **kwargs):
        """ update the form class list """
        context.update(
            super(LetterClassView, self).get_extra_context(
                request, context, **kwargs))
        if context[self.instance_name].get_STARS_rating().name != 'Reporter':
            letter_form_class = LetterStatusForm
        else:
            letter_form_class = LetterForm

        self.form_class_list.append({
                                        'form_name': 'letter_form',
                                        'form_class': letter_form_class,
                                        'instance_name': 'active_submission',
                                        'has_upload': True
                                    })

        # add the institution to the context
        return {'institution': context['active_submission'].institution,}

    def get_success_response(self, request, context):
        # self.save_form(form, request, context)
        return HttpResponseRedirect(
            reverse('submit-finalize',
                    kwargs={'institution_slug': self.get_institution().slug,
                            'submissionset': self.get_submissionset().id}))

# The second view of the submission process
submit_letter = LetterClassView("tool/submissions/submit_letter.html")


class FinalizeClassView(SubmitForRatingMixin, FormActionView):
    """
        Extends the Form class-based view from apps.helpers
    """
    def save_form(self, form, request, context):
        """ Finalizes the submission object """
        instance = context[self.instance_name]
        instance.date_submitted = date.today()
        instance.rating = instance.get_STARS_rating()
        instance.status = 'r'
        instance.submitting_user = request.user
        instance.save()

    def get_form_kwargs(self, request, context):
        """ Remove 'instance' from ``kwargs`` """
        kwargs = super(FinalizeClassView, self).get_form_kwargs(request, context)
        if kwargs.has_key('instance'):
            del kwargs['instance']
        return kwargs

    def get_success_action(self, request, context, form):

        self.save_form(form, request, context)
        ss = context[self.instance_name]

        # Send email to submitting institution
        _context = context
        _context.update({'submissionset': ss,})

        et = EmailTemplate.objects.get(slug="submission_for_rating")
        et.send_email([ss.institution.contact_email,], {'submissionset': ss,})

        ss.institution.current_subscription.ratings_used += 1
        ss.institution.current_subscription.save()

        ss.institution.current_rating = ss.rating
        ss.institution.rated_submission = ss
        ss.institution.save()

        # Send certificate to Marnie
        send_certificate_pdf.delay(ss)

        # update their current submission
        rollover_submission.delay(ss)

        return respond(request, 'tool/submissions/submit_success.html',
                       { 'institution': ss.institution,
                         'submissionset': ss })

# The final step of the submission process
submit_finalize = FinalizeClassView("tool/submissions/submit_finalize.html",
                                    Confirm,
                                    instance_name='active_submission',
                                    form_name='object_form')

def _get_category_submission_context(request, submissionset, category_id):

    submissionset_obj = get_object_or_404(SubmissionSet, id=submissionset)

    # confirm that the category exists...
    category = get_object_or_404(Category, id=category_id,
                                 creditset=submissionset_obj.creditset)

    # ... and get the related CategorySubmission
    # @TODO consider a transaction here
    try:
        category_submission = CategorySubmission.objects.get(
            submissionset=submissionset_obj, category=category)
    except CategorySubmission.DoesNotExist:
        category_submission = CategorySubmission(
            submissionset=submissionset_obj, category=category)
        category_submission.save()

    context={
        'active_submission': submissionset_obj,
        'creditset': submissionset_obj.creditset,
        'category': category,
        'category_submission': category_submission,
        'submissionset_id': submissionset
    }
    return context

def _get_subcategory_submission_context(request, submissionset, category_id,
                                        subcategory_id):

    context = _get_category_submission_context(request=request,
                                               submissionset=submissionset,
                                               category_id=category_id)

    category_submission=context.get('category_submission')
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)

    # get the related SubcategorySubmission
    try:
        subcategory_submission = SubcategorySubmission.objects.get(
            category_submission=category_submission, subcategory=subcategory)
    except SubcategorySubmission.DoesNotExist:
        subcategory_submission = SubcategorySubmission(
            category_submission=category_submission, subcategory=subcategory)
        subcategory_submission.save()

    context.update({
        'subcategory': subcategory,
        'subcategory_submission': subcategory_submission,
    })
    return context

@user_has_tool
def subcategory_detail(request, institution_slug, submissionset,
                       category_id, subcategory_id):

    """
        The sub-category summary page for a submission
    """
    context = _get_subcategory_submission_context(
        request=request,
        submissionset=submissionset,
        category_id=category_id,
        subcategory_id=subcategory_id)
    context['institution_slug'] = institution_slug
    subcategory = context.get('subcategory')
    subcategory_submission = context.get('subcategory_submission')

    # process the description form
    (submission_form, saved) = basic_save_form(
        request, subcategory_submission, '', SubcategorySubmissionForm,
        fail_msg="Description has <b>NOT BEEN SAVED</b>! Please correct "
                 "the errors below.")

    errors = request.method == "POST" and not saved

    if saved:
        return HttpResponseRedirect(
            subcategory_submission.category_submission.get_submit_url())

    context.update({'subcategory': subcategory,
                    'submission_form': submission_form, 'errors': errors})

    return respond(request, "tool/submissions/subcategory.html", context)

def _get_credit_submission_context(request, submissionset, category_id,
                                   subcategory_id, credit_id):

    context = _get_subcategory_submission_context(
        request=request,
        submissionset=submissionset,
        category_id=category_id,
        subcategory_id=subcategory_id)

    subcategory_submission = context.get('subcategory_submission')
    credit = get_object_or_404(Credit, id=credit_id)
    # get the related CreditSubmission
    try:
        credit_submission = CreditUserSubmission.objects.get(
            subcategory_submission=subcategory_submission, credit=credit)
    except CreditUserSubmission.DoesNotExist:
        credit_submission = CreditUserSubmission(
            subcategory_submission=subcategory_submission, credit=credit,
            user=request.user)
        credit_submission.save()

    credit_submission.user = request.user

    context.update({
        'credit': credit,
        'credit_submission': credit_submission,
    })
    return context

@user_has_tool
def credit_detail(request, institution_slug, submissionset, category_id,
                  subcategory_id, credit_id):
    """
        Submit all reporting fields and other forms for a specific credit
    """
    context = _get_credit_submission_context(request=request,
                                             submissionset=submissionset,
                                             category_id=category_id,
                                             subcategory_id=subcategory_id,
                                             credit_id=credit_id)
    credit_submission = context.get('credit_submission')
    # Build and process the Credit Submission form
    # CAUTION: onload handler in the template assumes this form has no prefix!!
    (submission_form, saved) = basic_save_form(
        request, credit_submission, '', CreditUserSubmissionForm,
        fail_msg="Credit data has <b>NOT BEEN SAVED</b>! Please correct "
        "the errors below.")

    errors = request.method == "POST" and not saved

    # load any warnings (generated by custom validation) onto the form
    if request.method == 'GET' and credit_submission.is_complete():
        # warnings are loaded during validation for POST's
        submission_form.load_warnings()
    if submission_form.has_warnings():
        # Duplicate code: this warning message is duplicated in test
        # case submission view
        messages.info(request,
                      "Some data values are not within the expected range "
                      "- see notes below.")

    context.update({'submission_form': submission_form, 'errors': errors,})

    return respond(request, "tool/submissions/credit_reporting_fields.html",
                   context)

@user_has_tool
def credit_documentation(request, institution_slug, submissionset,
                         category_id, subcategory_id, credit_id):
    """
        Credit documentation
    """
    context = _get_credit_submission_context(request=request,
                                             submissionset=submissionset,
                                             category_id=category_id,
                                             subcategory_id=subcategory_id,
                                             credit_id=credit_id)

    popup = request.GET.get('popup', False)
    template = ("tool/submissions/credit_info_popup.html" if popup
                else "tool/submissions/credit_info.html")
    return respond(request, template, context)

@user_has_tool
def credit_notes(request, institution_slug, submissionset,
                 category_id, subcategory_id, credit_id):
    """
        Internal notes for the credit submission
    """
    context = _get_credit_submission_context(request=request,
                                             submissionset=submissionset,
                                             category_id=category_id,
                                             subcategory_id=subcategory_id,
                                             credit_id=credit_id)
    credit_submission = context.get('credit_submission')
    # Build and process the Credit Submission Notes form
    (notes_form, saved) = basic_save_form(request, credit_submission, '',
                                          CreditUserSubmissionNotesForm)

    context.update({'notes_form': notes_form,})

    return respond(request, "tool/submissions/credit_notes.html", context)

@user_has_tool
def add_responsible_party(request, institution_slug, submissionset):
    """
        Provides a pop-up form for adding a new ResponsibleParty to an
        institution and updates the dropdown on the credit submission
        page
    """
    current_inst = get_object_or_404(Institution, slug=institution_slug)

    responsible_party = ResponsibleParty(institution=current_inst)

    (responsible_party_form, saved) = basic_save_new_form(request,
                                                          responsible_party,
                                                          'new_rp',
                                                          ResponsiblePartyForm)

    if saved:
        context = {'id': responsible_party.id, 'name': responsible_party,}
        return respond(request,
                       "tool/submissions/responsible_party_redirect.html",
                       context)

    context = {'responsible_party_form': responsible_party_form,}

    return respond(request, "tool/submissions/responsible_party.html", context)

def serve_uploaded_file(request, institution_slug, submissionset,
                        inst_id, path):
    """
        Serves file submissions.
    """
    _ = get_object_or_404(Institution, slug=institution_slug)

    # @todo: this should get the upload submission object and use its
    # path property to server the file thus eliminating the implicit
    # coupling here with the upload_path_callback in the model.
    stored_path = "secure/%s/%s" % (inst_id, path)

    from django.views.static import serve
    return serve(request, stored_path, document_root=settings.MEDIA_ROOT)

def delete_uploaded_file_gateway(request, institution_slug, submissionset,
                                 inst_id, creditset_id, credit_id,
                                 field_id, filename):
    """
        Handles secure AJAX delete of uploaded files.

        We don't actually use the filename - rather we load the
        submission object and get the path from it.
    """
    current_inst = get_object_or_404(Institution, slug=institution_slug)

    if not user_can_edit_submission(request.user,
                                    current_inst.get_active_submission()):
        raise Http404

    if not current_inst or current_inst.id != int(inst_id):
        raise PermissionDenied("File not found")
    active_submission = current_inst.get_active_submission()

    credit_submission = get_object_or_404(
        CreditUserSubmission,
        credit__id=credit_id,
        subcategory_submission__category_submission__submissionset=active_submission)
    upload_submission = get_object_or_404(UploadSubmission,
                                          documentation_field__id=field_id,
                                          credit_submission = credit_submission)

    # Finally, perform the delete.  Let any exceptions simply cascade
    # up - they'll get logged.
    upload_submission.delete()

    return render_to_response('tool/submissions/delete_file.html',
                              {'filename':filename})
