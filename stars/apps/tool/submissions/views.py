from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect

from datetime import datetime

from stars.apps.auth.utils import respond
from stars.apps.auth.decorators import user_can_submit, user_is_inst_admin
from stars.apps.submissions.models import *
from stars.apps.tool.submissions.forms import *
from stars.apps.credits.models import *
from stars.apps.helpers.forms.form_helpers import basic_save_form, basic_save_new_form
from stars.apps.tool.submissions.forms import CreditUserSubmissionForm, CreditUserSubmissionNotesForm, ResponsiblePartyForm

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
    }
    
    return respond(request, "tool/submissions/summary.html", context)

@user_is_inst_admin
def submit_confirm(request):
    """
        Provides a form for users to submit their submissionset
    """
    submission = _get_active_submission(request)
    if not submission:
        flashMessage.send("No active submission found to submit.", flashMessage.NOTICE)
        return HttpResponseRedirect("/tool/manage/submissionsets/")
        
    # Find all Credits listed as "In Progress"
    credit_list = [] 
    for cat in submission.categorysubmission_set.all():
            for sub in cat.subcategorysubmission_set.all():
                for c in sub.creditusersubmission_set.all():
                    if c.submission_status == 'p' or c.submission_status == 'ns':
                        credit_list.append(c)
    
    form = BoundaryForm(instance=submission)
    if request.method == 'POST':
        form = BoundaryForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save()
            return HttpResponseRedirect("/tool/submissions/submit/finalize/")
        else:
            flashMessage.send("Please correct the errors below.", flashMessage.ERROR)
            
    context = {
        'active_submission': submission,
        'credit_list': credit_list,
        'object_form': form,
    }
    template = "tool/submissions/submit_confirm.html"
    return respond(request, template, context)

@user_is_inst_admin
def submit_finalize(request):
    """
        Finalizes a submission
    """
    submission = _get_active_submission(request)
    if not submission:
        flashMessage.send("No active submission found to submit.", flashMessage.NOTICE)
        return HttpResponseRedirect("/tool/manage/submissionsets/")
        
    if submission.get_STARS_rating().name == 'Reporter':
        formClass = FinalizeForm
    else:
        formClass = FinalizeStatusForm
    
    form = formClass(instance=submission)
    if request.method == 'POST':
        form = formClass(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.date_submitted = datetime.now()
            submission.status = 'pr'
            submission.save()
            submission.institution.state.delete() # remove this submissionset as the active submissionset
            return respond(request, 'tool/submissions/submit_success.html', {})
        else:
            flashMessage.send("Please correct the errors below.", flashMessage.ERROR)
    context = {
        'active_submission': submission,
        'object_form': form,
    }
    template = "tool/submissions/submit_finalize.html"
    return respond(request, template, context)

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
        
@user_can_submit
def category_detail(request, category_id):
    """
        The category summary page for a submission
    """    
    context = _get_category_submission_context(request, category_id)
    category = context.get('category')
    category_submission = context.get('category_submission')
    
    subcategory_submission_list = []
    for subcategory in category.subcategory_set.all():
        try:
            subcategory_submission = SubcategorySubmission.objects.get(subcategory=subcategory, category_submission=category_submission)
        except SubcategorySubmission.DoesNotExist:
            subcategory_submission = SubcategorySubmission(subcategory=subcategory, category_submission=category_submission)
            subcategory_submission.save()
        subcategory_submission_list.append(subcategory_submission)
    
    context.update({
        'subcategory_submission_list': subcategory_submission_list,
    })
    
    return respond(request, "tool/submissions/category.html", context)


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

@user_can_submit
def subcategory_detail(request, category_id, subcategory_id):
    """
        The sub-category summary page for a submission
    """
    context = _get_subcategory_submission_context(request, category_id, subcategory_id)
    subcategory = context.get('subcategory')
    subcategory_submission = context.get('subcategory_submission')
    
    # get the related CreditSubmissions
    credit_submission_list = []
    for credit in subcategory.credit_set.all():
        try:
            credit_submission = CreditUserSubmission.objects.get(credit=credit, subcategory_submission=subcategory_submission)
        except CreditUserSubmission.DoesNotExist:
            credit_submission = CreditUserSubmission(credit=credit, subcategory_submission=subcategory_submission)
            credit_submission.submission_status = 'p'
            credit_submission.save()
        credit_submission_list.append(credit_submission)
    
    context.update({'credit_submission_list': credit_submission_list})
    
    return respond(request, "tool/submissions/subcategory.html", context)


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
        Finally, the credit submission form itself!!
    """
    context = _get_credit_submission_context(request, category_id, subcategory_id, credit_id)
    credit_submission = context.get('credit_submission')
    # Build and process the Credit Submission form
    # CAUTION: onload handler in the template assumes this form has no prefix!!
    (submission_form, saved) = basic_save_form(request, credit_submission, '', CreditUserSubmissionForm)
    
    # load any warnings (generated by custom validation) onto the form
    if request.method == 'GET' and credit_submission.is_complete():  # warnings are loaded during validation for POST's
        submission_form.load_warnings()
    if submission_form.has_warnings():  # Duplicate code: this warning message is duplicated in test case submission view
        flashMessage.send("Some data values are not within the expected range - see notes below.", flashMessage.NOTICE)

    context.update({'submission_form': submission_form, })

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
    print "Serving File..."
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
    print "In gateway..."
    current_inst = request.user.current_inst
    if not current_inst or current_inst.id != int(inst_id):
        raise PermissionDenied("File not found")
 
    credit_submission = get_object_or_404(CreditUserSubmission, credit__id=credit_id, \
                                                                subcategory_submission__category_submission__submissionset__institution = current_inst)
    upload_submission = get_object_or_404(UploadSubmission, documentation_field__id=field_id, \
                                                            credit_submission = credit_submission)
    print "About to delete..."
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
