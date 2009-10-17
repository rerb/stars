from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from stars.apps.auth.utils import respond
from stars.apps.auth.decorators import user_is_inst_admin, user_is_staff
from stars.apps.auth import xml_rpc
from stars.apps.institutions.models import Institution, InstitutionState, StarsAccount
from stars.apps.submissions.models import SubmissionSet, Payment
from stars.apps.helpers.forms import form_helpers
from stars.apps.helpers import watchdog
from stars.apps.helpers import flashMessage
from stars.apps.dashboard.manage.forms import *
    
@user_is_inst_admin
def institution_detail(request):
    """
        Display the Institution Form so user can edit basic info about their institution
    """
    current_inst = request.user.current_inst
    
    if request.user.is_staff:
        FormClass = AdminInstitutionForm
    else:
        FormClass = InstitutionContactForm
        
    (institution_form,saved) = form_helpers.basic_save_form(request, current_inst, str(current_inst.id), FormClass)
                
    context = {'institution_form': institution_form}
    return respond(request, 'dashboard/manage/detail.html', context)
    
@user_is_inst_admin
def institution_payments(request):
    """
        Display a list of payments made by the institution
    """
    current_inst = request.user.current_inst
    
    payment_list = Payment.objects.filter(submissionset__institution=current_inst)
    
    context = {'payment_list': payment_list}
    return respond(request, 'dashboard/manage/payments.html', context)
    
@user_is_inst_admin
def accounts(request):
    """
        Provides an interface to manage user accounts for an institution.
    """
    # most of the context for this view comes from the request.user object!
    account_form = AccountForm()
    
    return respond(request, 'dashboard/manage/accounts.html', {'account_form': account_form})

@user_is_inst_admin
def add_account(request):
    """
        Provides an interface to add user accounts to an institution.
    """
    current_inst = request.user.current_inst
    
    if request.method == 'POST':
        account_form = AccountForm(request.POST)
        if account_form.is_valid():
            # Get the AASHE account info for this email
            user_list = xml_rpc.get_user_by_email(account_form.cleaned_data['email'])
            if not user_list:
                flashMessage.send("AASHE has no users with e-mail: %s."%account_form.cleaned_data['email'], flashMessage.ERROR)
                account_form._errors['email'] = ErrorList(["No AASHE account found"])
            else:
                user = xml_rpc.get_user_from_user_dict(user_list[0], None)
                try:
                    # See if there is already a STARS Account
                    account = StarsAccount.objects.get(user=user, institution=current_inst)
                    account.user_level = account_form.cleaned_data['userlevel']
                except StarsAccount.DoesNotExist:
                    # Or create one
                    account = StarsAccount(user=user, institution=current_inst, user_level=account_form.cleaned_data['userlevel'])
                account.save()
                return HttpResponseRedirect(settings.MANAGE_USERS_URL)
    else:
        account_form = AccountForm()
    
    return respond(request, 'dashboard/manage/add_account.html', {'account_form': account_form})

@user_is_inst_admin
def delete_account(request, account_id):
    """
        Deletes a user account (user-institution relation)
    """
    # The account must be an account current user is allowed to manage!
    # Just give a 404 if the account_id doesn't belong to the user's institution
    account = get_object_or_404(StarsAccount, id=account_id, institution=request.user.current_inst)
    
    (form, deleted) = form_helpers.confirm_delete_form(request, account)       
    if deleted:
        watchdog.log('Inst. Admin', "Account: %s deleted.", watchdog.NOTICE)
        return HttpResponseRedirect(settings.MANAGE_USERS_URL)
    
    return respond(request, 'dashboard/manage/delete_account.html', {'account':account, 'confirm_delete_form': form})

    
@user_is_inst_admin
def submissionsets(request):
    """
        Provides an interface to manage submission sets for an institution
        and select indicate which one is the active submission
    """
    current_inst = request.user.current_inst
    
    active_set = current_inst.get_active_submission()
    
    return respond(request, 'dashboard/manage/submissionset_list.html', {'active_set': active_set})
    
        
@user_is_staff
def add_submissionset(request):
    """
        Provides a form for adding a new submission set
    """
    
    current_inst = request.user.current_inst
    
    # Build and precess the form for adding a new submission set
    new_set = SubmissionSet(institution=current_inst)
    
    ObjectForm = AdminSubmissionSetForm
    # if request.user.is_staff:
    #    ObjectForm = AdminSubmissionSetForm
    # else:
    #    Eventuatlly, this should lead user through a submission set purchase process (ticket #264)
    
    (object_form, saved) = form_helpers.basic_save_new_form(request, new_set, 'new_set', ObjectForm)
    if saved:
        # if this was the first one created then it should be active
        if current_inst.get_active_submission() is None:
            current_inst.set_active_submission(new_set)
        return HttpResponseRedirect(settings.MANAGE_SUBMISSION_SETS_URL)
    
    template = 'dashboard/manage/add_submissionset.html'
    context = {
        "object_form": object_form,
    }
    return respond(request, template, context)
    
@user_is_staff
def edit_submissionset(request, set_id):
    """
        Provides a form to edit a submission set
    """
    
    current_inst = request.user.current_inst
    
    submission_set = get_object_or_404(SubmissionSet, id=set_id, institution=current_inst)
    
    ObjectForm = AdminSubmissionSetForm
    if request.user.is_staff:
        ObjectForm = AdminSubmissionSetForm
    
    object_form, saved = form_helpers.basic_save_form(request, submission_set, set_id, ObjectForm)

    #print "date for %s is %s"%(current_inst, current_inst.state.active_submission_set.date_registered)
    #print "   saved: %s"%submission_set.date_registered
    ## test case above shows that related field can get out-of-sync with DB
    ## I think this is because the related field is cached with current_inst in the session, but that's a guess. 
    
    template = 'dashboard/manage/edit_submissionset.html'
    context = {
        "object_form": object_form,
    }
    return respond(request, template, context)

@user_is_inst_admin
def activate_submissionset(request, set_id):
    """
        Set the selected submission set as active
    """
    
    current_inst = request.user.current_inst
    
    submission_set = get_object_or_404(SubmissionSet, id=set_id)
    
    current_inst.set_active_submission(submission_set)
    
    return HttpResponseRedirect(settings.MANAGE_SUBMISSION_SETS_URL)
