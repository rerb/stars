from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.template import Context, loader, Template
from django.core.mail import send_mail

from datetime import datetime

from stars.apps.helpers.forms.views import *
from stars.apps.auth.utils import respond
from stars.apps.auth.decorators import user_can_submit, user_is_inst_admin
from stars.apps.auth.mixins import PermMixin, SubmissionMixin
from stars.apps.submissions.models import *
from stars.apps.cms.xml_rpc import get_article
from stars.apps.tool.my_submission.forms import *
from stars.apps.credits.models import *
from stars.apps.helpers.forms.form_helpers import basic_save_form, basic_save_new_form
from stars.apps.helpers.forms.forms import Confirm
from stars.apps.helpers import flashMessage
from stars.apps.tool.my_submission.forms import CreditUserSubmissionForm, CreditUserSubmissionNotesForm, ResponsiblePartyForm

def _get_active_submission(request):
    current_inst = request.user.current_inst
    active_submission = current_inst.get_active_submission() if current_inst else None
    if active_submission:
        # We populate this now to prevent two queries in the template
        # @todo - perhaps we should be doing this only when a credit set becomes active?
        init_credit_submissions(active_submission)
     
    return active_submission

@user_can_submit
def summary(request):
    """
        The entry page showing a grand summary of the submission
    """
    active_submission = _get_active_submission(request)
    category_submission_list = []
    if active_submission:
        category_submission_list = active_submission.categorysubmission_set.all()
        
    is_admin = request.user.has_perm('admin')
    
    context={
        'active_submission': active_submission,
        'category_submission_list': category_submission_list,
        'is_admin': is_admin,
        'summary': True,
    }
    
    return respond(request, "tool/submissions/summary.html", context)

class SubmissionClassView(SubmissionMixin, PermMixin, FormActionView):
    """
        Extends ``FormActionView`` to provide the class with the model instance
    """
    perm_list = ['admin',]
    perm_message = "Sorry, only administrators can submit for a rating."
    
    def get_extra_context(self, request, *args, **kwargs):
        """ Extend this method to add any additional items to the context """
        return {self.instance_name: _get_active_submission(request),}
    
    def get_instance(self, request, context, *args, **kwargs):
        """ Get's the active submission from the request """
        if context.has_key(self.instance_name):
            return context[self.instance_name]
        return None

class ConfirmClassView(SubmissionClassView):
    """
        The first step in the final submission process
    """
    
    def get_extra_context(self, request, *args, **kwargs):
        """ Extend this method to add any additional items to the context """
        
        _context = super(ConfirmClassView, self).get_extra_context(request, *args, **kwargs)
        # Find all Credits listed as "In Progress"
        credit_list = [] 
        for cat in _context[self.instance_name].categorysubmission_set.all():
                for sub in cat.subcategorysubmission_set.all():
                    for c in sub.creditusersubmission_set.all():
                        if c.submission_status == 'p' or c.submission_status == 'ns':
                            credit_list.append(c)
        _context.update({'credit_list': credit_list,})
        return _context
        
    def get_success_action(self, request, context, form):
        self.save_form(form, request, context)
        return HttpResponseRedirect("/tool/submissions/submit/letter/")

# The first submission view
submit_confirm = ConfirmClassView("tool/submissions/submit_confirm.html", BoundaryForm,  form_name='object_form', instance_name='active_submission')

class LetterClassView(SubmissionClassView):
    """
        Extends the Form class-based view from apps.helpers
    """
    
    def get_form_class(self, context, *args, **kwargs):
        """ This form gives institutions the option to choose Reporter status """
        if context[self.instance_name].get_STARS_rating().name != 'Reporter':
            return LetterStatusForm
        #return SubmissionClassView.get_form_class(self, *args, **kwargs)
        return super(LetterClassView, self).get_form_class(context, *args, **kwargs)
        
    def get_success_action(self, request, context, form):
        self.save_form(form, request, context)
        return HttpResponseRedirect("/tool/submissions/submit/finalize/")

# The second view of the submission process
submit_letter = LetterClassView("tool/submissions/submit_letter.html", LetterForm,  form_name='object_form', instance_name='active_submission', has_upload=True)

class FinalizeClassView(SubmissionClassView):
    """
        Extends the Form class-based view from apps.helpers
    """
    
    def save_form(self, form, request, context):
        """ Finalizes the submission object """
        instance = context[self.instance_name]
        instance.date_submitted = datetime.now()
        instance.status = 'pr'
        # instance.rating = self.instance.get_STARS_rating()
        instance.submitting_user = request.user
        instance.save()
        # instance.institution.state.delete() # remove this submissionset as the active submissionset
        
    def get_form_kwargs(self, request, context):
        """ Remove 'instance' from ``kwargs`` """
        kwargs = SubmissionClassView.get_form_kwargs(self, request, context)
        if kwargs.has_key('instance'):
            del kwargs['instance']
            # kwargs['instance'] = None
        return kwargs
    
    def get_success_action(self, request, context, form):
        
        self.save_form(form, request, context)
        
        t = loader.get_template('tool/submissions/submit_email.txt')
        _context = context
        _context.update({'submissionset': context[self.instance_name],})
        c = Context(_context)
        message = t.render(c)
        send_mail(  "Your STARS Submission",
                    message,
                    settings.EMAIL_HOST_USER,
                    [context[self.instance_name].institution.contact_email,],
                    fail_silently=False
                    )
        
        send_mail(  "STARS Submission!! (%s)" % context[self.instance_name].institution,
                    "%s has submitted for a rating! Time to review!" % context[self.instance_name],
                    settings.EMAIL_HOST_USER,
                    ['stars_staff@aashe.org','jesse@aashe.org'],
                    fail_silently=False
                    )
        
        return respond(request, 'tool/submissions/submit_success.html', {})
        
# The final step of the submission process
submit_finalize = FinalizeClassView("tool/submissions/submit_finalize.html",
                                    Confirm,
                                    instance_name='active_submission',
                                    form_name='object_form')

def _get_category_submission_context(request, category_id):
    active_submission = _get_active_submission(request)
    # confirm that the category exists... 
    category = get_object_or_404(Category, id=category_id)
    
    # ... and get the related CategorySubmission
    # @TODO consider a transaction here
    try:
        category_submission = CategorySubmission.objects.get(submissionset=active_submission, category=category)
    except CategorySubmission.DoesNotExist:
        category_submission = CategorySubmission(submissionset=active_submission, category=category)
        category_submission.save()
        
    context={        
        'active_submission': active_submission,
        'creditset': active_submission.creditset,
        'category': category,
        'category_submission': category_submission,
    }
    return context
        
#@user_can_submit
#def category_detail(request, category_id):
#    """
#        The category summary page for a submission
#    """    
#    context = _get_category_submission_context(request, category_id)
#    category = context.get('category')
#    category_submission = context.get('category_submission')
#    
#    subcategory_submission_list = []
#    for subcategory in category.subcategory_set.all():
#        try:
#            subcategory_submission = SubcategorySubmission.objects.get(subcategory=subcategory, category_submission=category_submission)
#        except SubcategorySubmission.DoesNotExist:
#            subcategory_submission = SubcategorySubmission(subcategory=subcategory, category_submission=category_submission)
#            subcategory_submission.save()
#        subcategory_submission_list.append(subcategory_submission)
#    
#    context.update({
#        'subcategory_submission_list': subcategory_submission_list,
#    })
#    
#    return respond(request, "tool/submissions/category.html", context)


def _get_subcategory_submission_context(request, category_id, subcategory_id):
    context = _get_category_submission_context(request, category_id)
    
    category_submission=context.get('category_submission')
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
            
    # get the related SubcategorySubmission
    try:
        subcategory_submission = SubcategorySubmission.objects.get(category_submission=category_submission, subcategory=subcategory)
    except SubcategorySubmission.DoesNotExist:
        subcategory_submission = SubcategorySubmission(category_submission=category_submission, subcategory=subcategory)
        subcategory_submission.save()
            
    context.update({
        'subcategory': subcategory,
        'subcategory_submission': subcategory_submission,
    })
    return context
#
#@user_can_submit
#def subcategory_detail(request, category_id, subcategory_id):
#    """
#        The sub-category summary page for a submission
#    """
#    context = _get_subcategory_submission_context(request, category_id, subcategory_id)
#    subcategory = context.get('subcategory')
#    subcategory_submission = context.get('subcategory_submission')
#    
#    # get the related CreditSubmissions
#    credit_submission_list = []
#    for credit in subcategory.credit_set.all():
#        try:
#            credit_submission = CreditUserSubmission.objects.get(credit=credit, subcategory_submission=subcategory_submission)
#        except CreditUserSubmission.DoesNotExist:
#            credit_submission = CreditUserSubmission(credit=credit, subcategory_submission=subcategory_submission)
#            credit_submission.submission_status = 'p'
#            credit_submission.save()
#        credit_submission_list.append(credit_submission)
#    
#    context.update({'credit_submission_list': credit_submission_list})
#    
#    return respond(request, "tool/submissions/subcategory.html", context)


def _get_credit_submission_context(request, category_id, subcategory_id, credit_id):
    context = _get_subcategory_submission_context(request, category_id, subcategory_id)
    
    subcategory_submission = context.get('subcategory_submission')
    credit = get_object_or_404(Credit, id=credit_id)
    # get the related CreditSubmission
    try:
        credit_submission = CreditUserSubmission.objects.get(subcategory_submission=subcategory_submission, credit=credit)
    except CreditUserSubmission.DoesNotExist:
        credit_submission = CreditUserSubmission(subcategory_submission=subcategory_submission, credit=credit, user=request.user)
        credit_submission.save()

    credit_submission.user = request.user
    
    context.update({
        'credit': credit,
        'credit_submission': credit_submission,
    })
    return context
    
@user_can_submit
def credit_detail(request, category_id, subcategory_id, credit_id):
    """
        Submit all reporting fields and other forms for a specific credit
    """
    context = _get_credit_submission_context(request, category_id, subcategory_id, credit_id)
    credit_submission = context.get('credit_submission')
    # Build and process the Credit Submission form
    # CAUTION: onload handler in the template assumes this form has no prefix!!
    (submission_form, saved) = basic_save_form(request, credit_submission, '', CreditUserSubmissionForm, fail_msg="Credit data has <b>NOT BEEN SAVED</b>! Please correct the errors below.")
    
    errors = request.method == "POST" and not saved
    
    # load any warnings (generated by custom validation) onto the form
    if request.method == 'GET' and credit_submission.is_complete():  # warnings are loaded during validation for POST's
        submission_form.load_warnings()
    if submission_form.has_warnings():  # Duplicate code: this warning message is duplicated in test case submission view
        flashMessage.send("Some data values are not within the expected range - see notes below.", flashMessage.NOTICE)

    context.update({'submission_form': submission_form, 'errors': errors,})

    return respond(request, "tool/submissions/credit_reporting_fields.html", context)

@user_can_submit
def credit_documentation(request, category_id, subcategory_id, credit_id):
    """
        Credit documentation 
    """
    context = _get_credit_submission_context(request, category_id, subcategory_id, credit_id)
    
    popup = request.GET.get('popup', False)
    template = "tool/submissions/credit_info_popup.html" if popup else "tool/submissions/credit_info.html"
    return respond(request, template, context)

@user_can_submit
def credit_notes(request, category_id, subcategory_id, credit_id):
    """
        Internal notes for the credit submission
    """
    context = _get_credit_submission_context(request, category_id, subcategory_id, credit_id)
    credit_submission = context.get('credit_submission')
    # Build and process the Credit Submission Notes form
    (notes_form, saved) = basic_save_form(request, credit_submission, '', CreditUserSubmissionNotesForm)
    
    context.update({'notes_form': notes_form,})

    return respond(request, "tool/submissions/credit_notes.html", context)
    
@user_can_submit
def add_responsible_party(request):
    """
        Provides a pop-up form for adding a new ResponsibleParty to an institution
        and updates the dropdown on the credit submission page
    """
    current_inst = request.user.current_inst
    if not current_inst:
        return HttpResponse("No Institution Selected")
        
    responsible_party = ResponsibleParty(institution=current_inst)
    
    (responsible_party_form, saved) = basic_save_new_form(request, responsible_party, 'new_rp', ResponsiblePartyForm) 
    
    if saved:
        context = {'id': responsible_party.id, 'name': responsible_party,}
        return respond(request, "tool/submissions/responsible_party_redirect.html", context)
    
    context = {'responsible_party_form': responsible_party_form,}

    return respond(request, "tool/submissions/responsible_party.html", context)
    
def serve_uploaded_file(request, inst_id, path):
    """
        Serves file submissions.
    """
    current_inst = request.user.current_inst
    if not current_inst or current_inst.id != int(inst_id):
        raise PermissionDenied("File not found")
        
    # @todo: this should get the upload submission object and use its path property to server the file
    #        thus eliminating the implicit coupling here with the upload_path_callback in the model.
    stored_path = "secure/%s/%s" % (inst_id, path)
    
    from django.views.static import serve
    return serve(request, stored_path, document_root=settings.MEDIA_ROOT)
  
@user_can_submit
def delete_uploaded_file_gateway(request, inst_id, creditset_id, credit_id, field_id, filename):
    """
        Handles secure AJAX delete of uploaded files.
        We don't actually use the filename - rather we load the submission object and get the path from it.
    """

    current_inst = request.user.current_inst
    if not current_inst or current_inst.id != int(inst_id):
        raise PermissionDenied("File not found")
 
    credit_submission = get_object_or_404(CreditUserSubmission, credit__id=credit_id, \
                                                                subcategory_submission__category_submission__submissionset__institution = current_inst)
    upload_submission = get_object_or_404(UploadSubmission, documentation_field__id=field_id, \
                                                            credit_submission = credit_submission)

    # Finally, perform the delete.  Let any exceptions simply cascade up - they'll get logged.
    upload_submission.delete()
   
    return render_to_response('tool/submissions/delete_file.html', {'filename':filename})


def init_credit_submissions(submissionset):
    """ 
        Initializes all CreditUserSubmissions in a SubmissionSet
    """
    # Build the category list if necessary
    #if submissionset.creditset.category_set.count() > submissionset.categorysubmission_set.count():
    for category in submissionset.creditset.category_set.all():
        try:
            categorysubmission = CategorySubmission.objects.get(category=category, submissionset=submissionset)
        except:
            categorysubmission = CategorySubmission(category=category, submissionset=submissionset)
            categorysubmission.save()

        # Create SubcategorySubmissions if necessary
        #if category.subcategory_set.count() > categorysubmission.subcategorysubmission_set.count():
        for subcategory in categorysubmission.category.subcategory_set.all():
            try:
                subcategorysubmission = SubcategorySubmission.objects.get(subcategory=subcategory, category_submission=categorysubmission)
            except SubcategorySubmission.DoesNotExist:
                subcategorysubmission = SubcategorySubmission(subcategory=subcategory, category_submission=categorysubmission)
                subcategorysubmission.save()
            
            # Create CreditUserSubmissions if necessary
            #if subcategory.credit_set.count() > subcategorysubmission.creditusersubmission_set.count():
            for credit in subcategory.credit_set.all():
                try:
                    creditsubmission = CreditUserSubmission.objects.get(credit=credit, subcategory_submission=subcategorysubmission)
                except CreditUserSubmission.DoesNotExist:
                    creditsubmission = CreditUserSubmission(credit=credit, subcategory_submission=subcategorysubmission)
                    creditsubmission.save()
