from datetime import timedelta, datetime
import sys

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage

from stars.apps.accounts.utils import respond
from stars.apps.accounts.decorators import user_is_inst_admin, user_is_staff
from stars.apps.accounts import xml_rpc
from stars.apps.institutions.models import Institution, InstitutionState, StarsAccount
from stars.apps.submissions.models import SubmissionSet, Payment, EXTENSION_PERIOD, ExtensionRequest
from stars.apps.submissions.tasks import migrate_purchased_submission
from stars.apps.helpers.forms import form_helpers
from stars.apps.helpers import watchdog
from stars.apps.helpers import flashMessage
from stars.apps.tool.manage.forms import *
from stars.apps.registration.forms import PaymentForm, PayLaterForm
from stars.apps.registration.views import process_payment, get_payment_dict, _get_registration_price, init_submissionset
from stars.apps.submissions.tasks import perform_migration
    
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
def responsible_party_list(request):
    """
        Display a list of responsible parties for the institution
    """
    current_inst = request.user.current_inst

    context = {'current_inst': current_inst,}
    
    return respond(request, 'tool/manage/responsible_party_list.html', context)

@user_is_inst_admin
def edit_responsible_party(request, rp_id):
    """
        Edit an existing responsible party
    """
    current_inst = request.user.current_inst
    rp = get_object_or_404(ResponsibleParty, institution=current_inst, id=rp_id)

    (object_form, saved) = form_helpers.basic_save_form(request, rp, '', ResponsiblePartyForm)

    if saved:
        return HttpResponseRedirect("/tool/manage/responsible-parties/")
    
    credit_list = rp.creditusersubmission_set.order_by('credit__subcategory').exclude(subcategory_submission__category_submission__submissionset__is_visible=False)
    
    context = {'responsible_party': rp, 'object_form': object_form, 'title': "Edit Responsible Party", 'credit_list': credit_list}
    return respond(request, 'tool/manage/edit_responsible_party.html', context)

@user_is_inst_admin
def add_responsible_party(request):
    """
        Edit an existing responsible party
    """
    current_inst = request.user.current_inst
    new_rp = ResponsibleParty(institution=current_inst)
    
    (object_form, saved) = form_helpers.basic_save_new_form(request, new_rp, 'new_rp', ResponsiblePartyForm)
    
    if saved:
        return HttpResponseRedirect("/tool/manage/responsible-parties/")
    
    context = {'object_form': object_form, 'title': "Add Responsible Party"}
    return respond(request, 'tool/manage/edit_responsible_party.html', context)

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
    
    latest_creditset = CreditSet.objects.get_latest()
    
    context = {'active_set': active_set, 'is_admin': is_admin, 'latest_creditset': latest_creditset}
    return respond(request, 'tool/manage/submissionset_list.html', context)

@user_is_inst_admin
def migrate_submissionset(request, set_id):
    """
        Provides a tool to migrate a submission set
    """
    
    current_inst = request.user.current_inst    
    submission_set = get_object_or_404(SubmissionSet, id=set_id, institution=current_inst)
    latest_creditset = CreditSet.objects.get_latest()
    
    if latest_creditset == submission_set.creditset:
        flashMessage.send("%s is the latest version of STARS" % (submission_set.creditset), flashMessage.ERROR)
        return HttpResponseRedirect("/tool/manage/submissionsets/")
    
    if submission_set.is_locked:
        flashMessage.send("Already marked for migration.", flashMessage.ERROR)
        return HttpResponseRedirect("/tool/manage/submissionsets/")
    
    ObjectForm = MigrateSubmissionSetForm
    
    object_form, saved = form_helpers.basic_save_form(request, submission_set, set_id, ObjectForm)
    if saved:
        # start a migration task
        perform_migration.delay(submission_set, latest_creditset, request.user)
        return HttpResponseRedirect("/tool/manage/submissionsets/")

    template = 'tool/manage/migrate_submissionset.html'
    context = {
        "object_form": object_form,
        "submission_set": submission_set,
        "latest_creditset": latest_creditset,
    }
    return respond(request, template, context)

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

def _gets_discount(institution, current_date=date.today()):
    """
        Get the latest submission prior to current_date
        that was either submitted or due before today
    """
    
    last_submission_date = None
    for ss in institution.submissionset_set.all():
        
        if ss.status == 'r':
            d = ss.date_submitted
        else:
            d = ss.submission_deadline
        
        if not last_submission_date or d > last_submission_date:
            last_submission_date = d
    
    if last_submission_date:
        
        # if they submitted or were due before feb 15th
        # then their deadline is May 15th
        if last_submission_date < date(year=2011, month=2, day=16):
            if current_date < date(year=2011, month=5, day=16):
                return True
    
        # or if last submission was less than 90 days ago
        td = timedelta(days=90)
        if current_date - last_submission_date <= td:
            return True
        
    return False

@user_is_inst_admin
def pay_submissionset(request, set_id):
    """
        Provides a payment form for those institutions that selected to pay later
    """
    current_inst = request.user.current_inst
    ss = get_object_or_404(SubmissionSet, id=set_id, institution=current_inst)
    is_member = current_inst.is_member_institution()
    amount = _get_registration_price(is_member)
    discount = _gets_discount(current_inst)
    if discount:
        amount = amount / 2
    
    pay_form = PaymentForm()
    
    if request.method == "POST":
        pay_form = PaymentForm(request.POST)
        if pay_form.is_valid():
            payment_dict = get_payment_dict(pay_form, current_inst)
            product_dict = {
                'price': amount,
                'quantity': 1,
                'name': "STARS Participant Registration",
            }
    
            result = process_payment(payment_dict, [product_dict], invoice_num=current_inst.aashe_id)
            if result.has_key('cleared') and result.has_key('msg'):
                if result['cleared'] and result['trans_id']:
                    p = Payment(
                                    submissionset=ss,
                                    date=datetime.now(),
                                    amount=amount,
                                    user=request.user,
                                    reason='reg',
                                    type='credit',
                                    confirmation=str(result['trans_id']),
                                )
                    p.save()
                    ss.institution.set_active_submission(ss)
                    return HttpResponseRedirect("/tool/manage/submissionsets/")
                else:
                    flashMessage.send("Processing Error: %s" % result['msg'], flashMessage.ERROR)
        else:
            flashMessage.send("Please correct the errors below", flashMessage.ERROR)
                    
    template = 'tool/manage/pay_submissionset.html'
    context = {
        "object_form": pay_form,
        "amount": amount,
        'is_member': is_member,
        'discount': discount,
    }
    return respond(request, template, context)

def send_exec_renew_email(institution):
            
    mail_to = [institution.executive_contact_email,]
    et = EmailTemplate.objects.get(slug="reg_renewal_exec")
    et.send_email(mail_to, {'institution': institution,})

@user_is_inst_admin
def purchase_submissionset(request):
    """
        Provides a view to allow institutions to purchase a new submission set
    """
    current_inst = request.user.current_inst
    is_member = current_inst.is_member_institution()
    amount = _get_registration_price(current_inst)
    discount = _gets_discount(current_inst)
    if discount:
        amount = amount / 2
    
    pay_form = PaymentForm()
    later_form = PayLaterForm()
    
    if request.method == "POST":
        
        migrate_message = "Your data is being migrated. It will appear shortly."
        
        later_form = PayLaterForm(request.POST)
        if later_form.is_valid() and later_form.cleaned_data['confirm']:
            
            old_ss = current_inst.get_latest_submission(include_unrated=True)
            ss = init_submissionset(current_inst, request.user, datetime.now())
            flashMessage.send(migrate_message, flashMessage.NOTICE)
            # Queue the task to handle the migration
            migrate_purchased_submission.delay(old_ss, ss)
            
            p = Payment(
                            submissionset=ss,
                            date=datetime.now(),
                            amount=amount,
                            user=request.user,
                            reason='reg',
                            type='later',
                            confirmation=None,
                        )
            p.save()
            
            if request.user.email != ss.institution.contact_email:
                mail_to = [request.user.email, ss.institution.contact_email]
            else:
                mail_to = [ss.institution.contact_email,]
            
            et = EmailTemplate.objects.get(slug="reg_renewal_unpaid")
            et.send_email(mail_to, {'amount': p.amount,})
            
            send_exec_renew_email(ss.institution)
            
            return HttpResponseRedirect("/tool/manage/submissionsets/")
        else:
            pay_form = PaymentForm(request.POST)
            if pay_form.is_valid():
                payment_dict = get_payment_dict(pay_form, current_inst)
                product_dict = {
                    'price': amount,
                    'quantity': 1,
                    'name': "STARS Participant Registration",
                }
        
                result = process_payment(payment_dict, [product_dict], invoice_num=current_inst.aashe_id)
                if result.has_key('cleared') and result.has_key('msg'):
                    if result['cleared'] and result['trans_id']:
                        
                        old_ss = current_inst.get_latest_submission(include_unrated=True)
                        ss = init_submissionset(current_inst, request.user, datetime.now())
                        flashMessage.send(migrate_message, flashMessage.NOTICE)
                        # Queue the task to handle the migration
                        migrate_purchased_submission.delay(old_ss, ss)
                        
                        p = Payment(
                                        submissionset=ss,
                                        date=datetime.now(),
                                        amount=amount,
                                        user=request.user,
                                        reason='reg',
                                        type='credit',
                                        confirmation=str(result['trans_id']),
                                    )
                        p.save()
                        
                        if request.user.email != ss.institution.contact_email:
                            mail_to = [request.user.email, ss.institution.contact_email]
                        else:
                            mail_to = [ss.institution.contact_email,]

                        et = EmailTemplate.objects.get(slug="reg_renewed_paid")
                        email_context = {'payment_dict': payment_dict,'institution': ss.institution, "payment": p}
                        et.send_email(mail_to, email_context)
                        
                        send_exec_renew_email(ss.institution)
                        
                        ss.institution.set_active_submission(ss)
                        
                        return HttpResponseRedirect("/tool/manage/submissionsets/")
                    else:
                        flashMessage.send("Processing Error: %s" % result['msg'], flashMessage.ERROR)
                else:
                    flashMessage.send("Please correct the errors below", flashMessage.ERROR)
                    
    template = 'tool/manage/purchase_submissionset.html'
    context = {
        "pay_form": pay_form,
        "later_form": later_form,
        "amount": amount,
        'is_member': is_member,
        'discount': discount,
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
