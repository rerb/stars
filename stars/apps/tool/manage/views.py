from datetime import timedelta, datetime, date
import sys

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage

from stars.apps.accounts.utils import respond
from stars.apps.accounts.decorators import user_is_staff
from stars.apps.accounts import xml_rpc
from stars.apps.institutions.models import Institution, StarsAccount, Subscription, SubscriptionPayment, SUBSCRIPTION_DURATION
from stars.apps.institutions.rules import user_has_access_level
from stars.apps.submissions.models import SubmissionSet, EXTENSION_PERIOD, ExtensionRequest
from stars.apps.submissions.tasks import migrate_purchased_submission, perform_migration
from stars.apps.third_parties.models import ThirdParty
from stars.apps.helpers.forms import form_helpers
from stars.apps.helpers import watchdog
from stars.apps.helpers import flashMessage
from stars.apps.tool.manage.forms import *
from stars.apps.registration.forms import PaymentForm, PayLaterForm
from stars.apps.registration.views import process_payment, get_payment_dict, _get_registration_price, init_submissionset
from stars.apps.notifications.models import EmailTemplate 
    
def _get_current_institution(request):
    if hasattr(request.user, 'current_inst'):
        if not user_has_access_level(request.user, 'admin', request.user.current_inst):
            raise PermissionDenied('Sorry, only institution administrators have access.')
        return request.user.current_inst
    else:
        raise Http404
    
def institution_detail(request):
    """
        Display the Institution Form so user can edit basic info about their institution
    """
    current_inst = _get_current_institution(request)
    
    if request.user.is_staff:
        FormClass = AdminInstitutionForm
    else:
        FormClass = InstitutionContactForm
        
    (institution_form,saved) = form_helpers.basic_save_form(request, current_inst, str(current_inst.id), FormClass)
                
    context = {'institution_form': institution_form}
    return respond(request, 'tool/manage/detail.html', context)
    
def institution_payments(request):
    """
        Display a list of payments made by the institution
    """
    current_inst = _get_current_institution(request)
    
    payment_list = SubscriptionPayment.objects.filter(subscription__institution=current_inst).order_by('-date')

    context = {
                'payment_list': payment_list,
              }
    return respond(request, 'tool/manage/payments.html', context)

def responsible_party_list(request):
    """
        Display a list of responsible parties for the institution
    """
    current_inst = _get_current_institution(request)

    context = {'current_inst': current_inst,}
    
    return respond(request, 'tool/manage/responsible_party_list.html', context)

def edit_responsible_party(request, rp_id):
    """
        Edit an existing responsible party
    """
    current_inst = _get_current_institution(request)
    rp = get_object_or_404(ResponsibleParty, institution=current_inst, id=rp_id)

    (object_form, saved) = form_helpers.basic_save_form(request, rp, '', ResponsiblePartyForm)

    if saved:
        return HttpResponseRedirect("/tool/manage/responsible-parties/")
    
    credit_list = rp.creditusersubmission_set.order_by('credit__subcategory__category__creditset', 'credit__subcategory').exclude(subcategory_submission__category_submission__submissionset__is_visible=False)
    
    context = {'responsible_party': rp, 'object_form': object_form, 'title': "Edit Responsible Party", 'credit_list': credit_list}
    return respond(request, 'tool/manage/edit_responsible_party.html', context)


def add_responsible_party(request):
    """
        Edit an existing responsible party
    """
    current_inst = _get_current_institution(request)
    new_rp = ResponsibleParty(institution=current_inst)
    
    (object_form, saved) = form_helpers.basic_save_new_form(request, new_rp, 'new_rp', ResponsiblePartyForm)
    
    if saved:
        return HttpResponseRedirect("/tool/manage/responsible-parties/")
    
    context = {'object_form': object_form, 'title': "Add Responsible Party"}
    return respond(request, 'tool/manage/edit_responsible_party.html', context)


def delete_responsible_party(request, rp_id):
    """
    Remove a responsible party if they aren't tied to any submissions
    """
    current_inst = _get_current_institution(request)
    rp = ResponsibleParty.objects.get(institution=current_inst, id=rp_id)

    credit_count = rp.creditusersubmission_set.exclude(subcategory_submission__category_submission__submissionset__is_visible=False).count()
    if credit_count > 0:
        flashMessage.send("This Responsible Party cannot be removed because he/she is listed with one or more credits.", flashMessage.ERROR)
        return HttpResponseRedirect(rp.get_manage_url())
    else:
        flashMessage.send("Succesfully Removed Responsible Party: %s" % rp, flashMessage.NOTICE)
        rp.delete()
        return HttpResponseRedirect("/tool/manage/responsible-parties/")


def accounts(request, account_id=None):
    """
        Provides an interface to manage user accounts for an institution.
        Supply an optional StarsAccount id to provide an edit form for that account.
    """
    current_inst = _get_current_institution(request)
    
    # create a list of accounts, one of which might have an 'edit' form
    account_list = []
    editing = False
    all_accounts = list(current_inst.starsaccount_set.all()) + list(current_inst.pendingaccount_set.all())
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


def add_account(request):
    """
        Provides an interface to add user accounts to an institution.
    """
    current_inst = _get_current_institution(request)

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

    

def delete_account(request, account_id):
    """
        Deletes a user account (user-institution relation)
    """
    current_inst = _get_current_institution(request)
    
    (preferences, notify_form) = _update_preferences(request)
    # Careful here - this needs to handle deletion of any type of account, real and pending.
    # The account must be an account current user is allowed to manage!
    # Just give a 404 if the account_id doesn't belong to the user's institution
    try:
        account = StarsAccount.objects.get(id=account_id, institution=current_inst)
    except StarsAccount.DoesNotExist:
        account = get_object_or_404(PendingAccount, id=account_id, institution=current_inst)   
        # no need to confirm deletion of pending accounts, since there is no consequence to doing so.
        account.delete()
        flashMessage.send("Pending account: %s successfully deleted."%account,flashMessage.SUCCESS)
        if preferences.notify_users:
            account.notify(StarsAccount.DELETE_ACCOUNT, request.user, current_inst)
        return HttpResponseRedirect(settings.MANAGE_USERS_URL)

    (form, deleted) = form_helpers.confirm_delete_form(request, account)       
    if deleted:
        watchdog.log('Manage Users', "Account: %s deleted."%account, watchdog.NOTICE)
        if preferences.notify_users:
            account.notify(StarsAccount.DELETE_ACCOUNT, request.user, current_inst)
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


def share_data(request):
    """
        I'm not exactly sure how this will tie into the API yet
        so this is really just a place-holder
    """
    current_inst = _get_current_institution(request)
    
    (object_form, saved) = form_helpers.basic_save_form(request, current_inst, '', ThirdPartiesForm)
    
    if saved:
        return HttpResponseRedirect("/tool/manage/share-data/")
    
    context = {
                'current_inst': current_inst,
                'object_form': object_form,
                'third_party_list': ThirdParty.objects.all(),
                'snapshot_list': SubmissionSet.objects.get_snapshots(current_inst),
            }
    return respond(request, 'tool/manage/third_parties.html', context)

#@user_is_staff
#def submissionsets(request):
#    """
#        Provides an interface to manage submission sets for an institution
#        and select indicate which one is the active submission
#    """
#    current_inst = _get_current_institution(request)
#    
#    active_set = current_inst.get_active_submission()
#    
#    is_admin = request.user.has_perm('admin')
#    
#    latest_creditset = CreditSet.objects.get_latest()
#    
#    context = {'active_set': active_set, 'is_admin': is_admin, 'latest_creditset': latest_creditset}
#    return respond(request, 'tool/manage/submissionset_list.html', context)


def migrate_submissionset(request):
    """
        Provides a tool to migrate a submission set
    """
    current_inst = _get_current_institution(request)
    current_submission = current_inst.current_submission
    latest_creditset = CreditSet.objects.get_latest()
    
    if latest_creditset == current_submission.creditset:
        flashMessage.send("%s is the latest version of STARS" % (current_submission.creditset), flashMessage.ERROR)
        return HttpResponseRedirect("/tool/submissions/")
    
    if current_submission.is_locked:
        flashMessage.send("Already marked for migration.", flashMessage.ERROR)
        return HttpResponseRedirect("/tool/")
    
    ObjectForm = MigrateSubmissionSetForm
    
    object_form, saved = form_helpers.basic_save_form(request, current_submission, current_submission.id, ObjectForm)
    if saved:
        # start a migration task
        flashMessage.send("Your migration is in progress.", flashMessage.SUCCESS)
        perform_migration.delay(current_submission, latest_creditset, request.user)
        return HttpResponseRedirect("/tool/")

    template = 'tool/manage/migrate_submissionset.html'
    context = {
        "object_form": object_form,
        "submission_set": current_submission,
        "latest_creditset": latest_creditset,
    }
    return respond(request, template, context)

#@user_is_staff
#def add_submissionset(request):
#    """
#        Provides a form for adding a new submission set
#    """
#    
#    current_inst = _get_current_institution(request)
#    
#    # Build and precess the form for adding a new submission set
#    new_set = SubmissionSet(institution=current_inst)
#    
#    ObjectForm = AdminSubmissionSetForm
#    # if request.user.is_staff:
#    #    ObjectForm = AdminSubmissionSetForm
#    # else:
#    #    Eventuatlly, this should lead user through a submission set purchase process (ticket #264)
#    
#    (object_form, saved) = form_helpers.basic_save_new_form(request, new_set, 'new_set', ObjectForm)
#    if saved:
#        # if this was the first one created then it should be active
#        if current_inst.get_active_submission() is None:
#            current_inst.set_active_submission(new_set)
#        return HttpResponseRedirect(settings.MANAGE_SUBMISSION_SETS_URL)
#    
#    template = 'tool/manage/add_submissionset.html'
#    context = {
#        "object_form": object_form,
#    }
#    return respond(request, template, context)

def _gets_discount(institution, current_date=date.today()):
    """
        Institutions get half-off their submission if their renewal
        within 90 days of their last subscription
    """
    
    last_subscription_end = institution.get_last_subscription_end()
    
    if last_subscription_end:
    
        # if last subscription end was less than 90 days ago
        # or it hasn't expired
        td = timedelta(days=90)
        if current_date <= last_subscription_end + td:
            return True
        
    return False


#def pay_submissionset(request, set_id):
#    """
#        Provides a payment form for those institutions that selected to pay later
#    """
#    current_inst = _get_current_institution(request)
#    ss = get_object_or_404(SubmissionSet, id=set_id, institution=current_inst)
#    is_member = current_inst.is_member_institution()
#    # get the amount of the pay_later payments
#    p = ss.payment_set.filter(type='later')[0]
#    amount = p.amount
#    discount = _gets_discount(current_inst)
#    if discount:
#        amount = amount / 2
#        if is_member:
#            reason = "member_renew"
#        else:
#            reason = "nonmember_renew"
#    else:
#        if is_member:
#            reason = "member_reg"
#        else:
#            reason = "nonmember_reg"
#        
#    pay_form = PaymentForm()
#    
#    if request.method == "POST":
#        pay_form = PaymentForm(request.POST)
#        if pay_form.is_valid():
#            payment_dict = get_payment_dict(pay_form, current_inst)
#            product_dict = {
#                'price': amount,
#                'quantity': 1,
#                'name': "STARS Participant Registration",
#            }
#    
#            result = process_payment(payment_dict, [product_dict], invoice_num=current_inst.aashe_id)
#            if result.has_key('cleared') and result.has_key('msg'):
#                if result['cleared'] and result['trans_id']:
#                    p = Payment(
#                                    submissionset=ss,
#                                    date=datetime.now(),
#                                    amount=amount,
#                                    user=request.user,
#                                    reason=reason,
#                                    type='credit',
#                                    confirmation=str(result['trans_id']),
#                                )
#                    p.save()
#                    ss.institution.set_active_submission(ss)
#                    return HttpResponseRedirect("/tool/manage/submissionsets/")
#                else:
#                    flashMessage.send("Processing Error: %s" % result['msg'], flashMessage.ERROR)
#        else:
#            flashMessage.send("Please correct the errors below", flashMessage.ERROR)
#                    
#    template = 'tool/manage/pay_submissionset.html'
#    context = {
#        "object_form": pay_form,
#        "amount": amount,
#        'is_member': is_member,
#        'discount': discount,
#    }
#    return respond(request, template, context)

def send_exec_renew_email(institution):
            
    mail_to = [institution.executive_contact_email,]
    et = EmailTemplate.objects.get(slug="reg_renewal_exec")
    et.send_email(mail_to, {'institution': institution,})

def purchase_subscription(request):
    """
        Provides a view to allow institutions to purchase a new subscription
    """
    current_inst = _get_current_institution(request)
    is_member = current_inst.is_member_institution()
    amount = _get_registration_price(current_inst, new=False)
    discount = _gets_discount(current_inst)
    if discount:
        amount = amount / 2
        if is_member:
            reason = "member_renew"
        else:
            reason = "nonmember_renew"
    else:
        if is_member:
            reason = "member_reg"
        else:
            reason = "nonmember_reg"
    
    pay_form = PaymentForm()
    
    if request.method == "POST":
        
        pay_form = PaymentForm(request.POST)
        if pay_form.is_valid():
            payment_dict = get_payment_dict(pay_form, current_inst)
            product_dict = {
                'price': amount,
                'quantity': 1,
                'name': "STARS Subscription Purchase",
            }
    
            result = process_payment(payment_dict, [product_dict], invoice_num=current_inst.aashe_id)
            if result.has_key('cleared') and result.has_key('msg'):
                if result['cleared'] and result['trans_id']:
                    
                    # calculate start date of subscription
                    start_date = current_inst.get_last_subscription_end()
                    if not start_date:
                        start_date = date.today()
                    else:
                        start_date += timedelta(days=1)
                    
                    sub = Subscription(
                                        institution=current_inst,
                                        start_date=start_date,
                                        end_date=start_date + timedelta(SUBSCRIPTION_DURATION),
                                        amount_due=0,
                                        paid_in_full=True,
                                       )
                    sub.save()
                    
                    p = SubscriptionPayment(
                                    subscription=sub,
                                    date=datetime.now(),
                                    amount=amount,
                                    user=request.user,
                                    reason=reason,
                                    method='credit',
                                    confirmation=str(result['trans_id']),
                                )
                    p.save()
                    
                    if request.user.email != current_inst.contact_email:
                        mail_to = [request.user.email, current_inst.contact_email]
                    else:
                        mail_to = [current_inst.contact_email,]

                    et = EmailTemplate.objects.get(slug="reg_renewed_paid")
                    email_context = {'payment_dict': payment_dict,'institution': current_inst, "payment": p}
                    et.send_email(mail_to, email_context)
                    
                    send_exec_renew_email(current_inst)
                    
                    current_inst.current_subscription = sub
                    current_inst.is_participant = True
                    current_inst.save()
                    
                    return HttpResponseRedirect("/tool/")
                else:
                    flashMessage.send("Processing Error: %s" % result['msg'], flashMessage.ERROR)
            else:
                flashMessage.send("Please correct the errors below", flashMessage.ERROR)
                    
    template = 'tool/manage/purchase_subscription.html'
    context = {
        "pay_form": pay_form,
        "amount": amount,
        'is_member': is_member,
        'discount': discount,
    }
    return respond(request, template, context)


#def extension_request(request, set_id):
#    
#    current_inst = _get_current_institution(request)
#    
#    ss = get_object_or_404(SubmissionSet, id=set_id, institution=current_inst)
#    
#    if not ss.can_apply_for_extension():
#        # how did they get to this page?
#        flashMessage.send("Sorry, extension requests to this submission set are not allowed at this time.", flashMessage.NOTICE)
#        watchdog.log('Extension Application', "Extension request denied." % ss, watchdog.ERROR)
#        return HttpResponseRedirect('/tool/manage/submissionsets/')
#    
#    object_form, confirmed = form_helpers.confirm_form(request)
#    
#    if confirmed:
#        er = ExtensionRequest(submissionset=ss, user=request.user)
#        er.old_deadline = ss.submission_deadline
#        er.save()
#        
#        td = EXTENSION_PERIOD
#        ss.submission_deadline += td
#        ss.save()
#        
#        flashMessage.send("Your extension request has been applied to your submission.", flashMessage.NOTICE)
#        return HttpResponseRedirect('/tool/manage/submissionsets/')
#
#    template = 'tool/manage/extension_request.html'
#    context = {
#        "object_form": object_form,
#    }
#    return respond(request, template, context)


#def activate_submissionset(request, set_id):
#    """
#        Set the selected submission set as active
#    """
#    
#    current_inst = _get_current_institution(request)
#    
#    submission_set = get_object_or_404(SubmissionSet, id=set_id)
#    
#    current_inst.set_active_submission(submission_set)
#    
#    return HttpResponseRedirect(settings.MANAGE_SUBMISSION_SETS_URL)

def boundary(request, set_id):
    """ Displays the Institution Boundary edit form """
    
    current_inst = _get_current_institution(request)
    submission_set = get_object_or_404(SubmissionSet, id=set_id)

    ObjectForm = BoundaryForm
    
    object_form, saved = form_helpers.basic_save_form(request, submission_set, submission_set.id, ObjectForm)

    template = 'tool/manage/boundary.html'
    context = {
        "object_form": object_form,
    }
    return respond(request, template, context)
