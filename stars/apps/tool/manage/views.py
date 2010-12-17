from datetime import timedelta

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from stars.apps.auth.utils import respond
from stars.apps.auth.decorators import user_is_inst_admin, user_is_staff
from stars.apps.auth import xml_rpc
from stars.apps.institutions.models import Institution, InstitutionState, StarsAccount
from stars.apps.submissions.models import SubmissionSet, Payment, EXTENSION_PERIOD, ExtensionRequest
from stars.apps.helpers.forms import form_helpers
from stars.apps.helpers import watchdog
from stars.apps.helpers import flashMessage
from stars.apps.tool.manage.forms import *
    
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
    return respond(request, 'tool/manage/detail.html', context)
    
@user_is_inst_admin
def institution_payments(request):
    """
        Display a list of payments made by the institution
    """
    current_inst = request.user.current_inst
    active_submission = current_inst.get_active_submission()
    
    payment_list = Payment.objects.filter(submissionset__institution=current_inst).exclude(type='later').order_by('-date')

    context = {'payment_list': payment_list, 
               'active_submission':active_submission,
              }
    return respond(request, 'tool/manage/payments.html', context)
    

@user_is_inst_admin
def accounts(request, account_id=None):
    """
        Provides an interface to manage user accounts for an institution.
        Supply an optional StarsAccount id to provide an edit form for that account.
    """
    # create a list of accounts, one of which might have an 'edit' form
    account_list = []
    editing = False
    all_accounts = list(request.user.current_inst.starsaccount_set.all()) + list(request.user.current_inst.pendingaccount_set.all())
    for account in all_accounts:
        if str(account.id) == str(account_id):  # this account should supply an editing form...
            editing = True
            edit_form = EditAccountForm(initial={'email':account.user.email, 'userlevel':account.user_level})
        else:
            edit_form = None 

        account_list.append({'account':account, 'edit_form':edit_form})

    if editing:
        new_account_form = DisabledAccountForm()
    else:
        new_account_form = AccountForm()

    (preferences, notify_form) = _update_preferences(request)
    
    context = {
               'account_list': account_list, 
               'new_account_form': new_account_form,
               'notify_form':notify_form,
               'editing': editing
              }
    return respond(request, 'tool/manage/accounts.html', context)

@user_is_inst_admin
def add_account(request):
    """
        Provides an interface to add user accounts to an institution.
    """
    current_inst = request.user.current_inst

    (preferences, notify_form) = _update_preferences(request)
    
    if request.method == 'POST':
        account_form = AccountForm(request.POST)
        if account_form.is_valid():
            # Get the AASHE account info for this email
            user_email = account_form.cleaned_data['email']
            user_level = account_form.cleaned_data['userlevel']
            user_list = xml_rpc.get_user_by_email(user_email)
            if not user_list:
                flashMessage.send("There is no AASHE user with e-mail: %s. STARS Account pending user's registration at www.aashe.org" % user_email, flashMessage.NOTICE)
                PendingAccount.update_account(request.user, preferences.notify_users, current_inst, user_level, user_email=user_email)
            else:
                user = xml_rpc.get_user_from_user_dict(user_list[0], None)
                StarsAccount.update_account(request.user, preferences.notify_users, current_inst, user_level, user=user)
            return HttpResponseRedirect(StarsAccount.get_manage_url())
    else:
        account_form = AccountForm()
    
    return respond(request, 'tool/manage/add_account.html', {'account_form': account_form, 'notify_form':notify_form,})

    
@user_is_inst_admin
def delete_account(request, account_id):
    """
        Deletes a user account (user-institution relation)
    """
    (preferences, notify_form) = _update_preferences(request)
    # Careful here - this needs to handle deletion of any type of account, real and pending.
    # The account must be an account current user is allowed to manage!
    # Just give a 404 if the account_id doesn't belong to the user's institution
    try:
        account = StarsAccount.objects.get(id=account_id, institution=request.user.current_inst)
    except StarsAccount.DoesNotExist:
        account = get_object_or_404(PendingAccount, id=account_id, institution=request.user.current_inst)   
        # no need to confirm deletion of pending accounts, since there is no consequence to doing so.
        account.delete()
        flashMessage.send("Pending account: %s successfully deleted."%account,flashMessage.SUCCESS)
        if preferences.notify_users:
            account.notify(StarsAccount.DELETE_ACCOUNT, request.user, request.user.current_inst)
        return HttpResponseRedirect(settings.MANAGE_USERS_URL)

    (form, deleted) = form_helpers.confirm_delete_form(request, account)       
    if deleted:
        watchdog.log('Manage Users', "Account: %s deleted."%account, watchdog.NOTICE)
        if preferences.notify_users:
            account.notify(StarsAccount.DELETE_ACCOUNT, request.user, request.user.current_inst)
        return HttpResponseRedirect(settings.MANAGE_USERS_URL)
    
    return respond(request, 'tool/manage/delete_account.html', {'account':account, 'confirm_form': form, 'notify_form':notify_form,})

def _update_preferences(request):
    """ 
        Helper method to DRY code around managing institution preferences 
        Returns (preferences, preferences_form)
    """
    try:
        preferences = request.user.current_inst.preferences
    except InstitutionPreferences.DoesNotExist:
        preferences = InstitutionPreferences(institution=request.user.current_inst)
    (notify_form,saved) = form_helpers.basic_save_form(request, preferences, '', NotifyUsersForm, flash_message=False)
    return (preferences, notify_form)
    
@user_is_inst_admin
def submissionsets(request):
    """
        Provides an interface to manage submission sets for an institution
        and select indicate which one is the active submission
    """
    current_inst = request.user.current_inst
    
    active_set = current_inst.get_active_submission()
    
    is_admin = request.user.has_perm('admin')
    
    return respond(request, 'tool/manage/submissionset_list.html', {'active_set': active_set, 'is_admin': is_admin})
    
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
    
    template = 'tool/manage/add_submissionset.html'
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

    template = 'tool/manage/edit_submissionset.html'
    context = {
        "object_form": object_form,
    }
    return respond(request, template, context)

@user_is_inst_admin
def extension_request(request, set_id):
    
    current_inst = request.user.current_inst
    
    ss = get_object_or_404(SubmissionSet, id=set_id, institution=current_inst)
    
    if not ss.can_apply_for_extension():
        # how did they get to this page?
        flashMessage.send("Sorry, extension requests to this submission set are not allowed at this time.", flashMessage.NOTICE)
        watchdog.log('Extension Application', "Extension request denied." % ss, watchdog.ERROR)
        return HttpResponseRedirect('/tool/manage/submissionsets/')
    
    object_form, confirmed = form_helpers.confirm_form(request)
    
    if confirmed:
        er = ExtensionRequest(submissionset=ss, user=request.user)
        er.old_deadline = ss.submission_deadline
        er.save()
        
        td = EXTENSION_PERIOD
        ss.submission_deadline += td
        ss.save()
        
        flashMessage.send("Your extension request has been applied to your submission.", flashMessage.NOTICE)
        return HttpResponseRedirect('/tool/manage/submissionsets/')

    template = 'tool/manage/extension_request.html'
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

@user_is_inst_admin
def boundary(request, set_id):
    """ Displays the Institution Boundary edit form """
    
    current_inst = request.user.current_inst
    submission_set = get_object_or_404(SubmissionSet, id=set_id)

    ObjectForm = BoundaryForm
    
    object_form, saved = form_helpers.basic_save_form(request, submission_set, submission_set.id, ObjectForm)

    template = 'tool/manage/boundary.html'
    context = {
        "object_form": object_form,
    }
    return respond(request, template, context)
