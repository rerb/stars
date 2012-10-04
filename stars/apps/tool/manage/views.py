from datetime import timedelta, datetime, date
from logging import getLogger

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied

from stars.apps.accounts.utils import respond
from stars.apps.accounts.decorators import user_is_inst_admin, user_has_tool
from stars.apps.accounts import xml_rpc
from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import StarsAccount, Subscription, \
     SubscriptionPayment, SUBSCRIPTION_DURATION, PendingAccount
from stars.apps.institutions.rules import user_has_access_level
from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.tasks import perform_migration, \
     perform_data_migration
from stars.apps.submissions.rules import user_can_migrate_version, \
     user_can_migrate_from_submission
from stars.apps.third_parties.models import ThirdParty
from stars.apps.helpers.forms import form_helpers

from stars.apps.tool.manage.forms import AdminInstitutionForm, \
     ParticipantContactForm, RespondentContactForm, ResponsibleParty, \
     ResponsiblePartyForm, DisabledAccountForm, \
     AccountForm, ThirdPartiesForm, InstitutionPreferences, \
     NotifyUsersForm, MigrateSubmissionSetForm, BoundaryForm

from stars.apps.registration.forms import PaymentForm, PayLaterForm
from stars.apps.registration.views import process_payment, get_payment_dict, \
     _get_registration_price
from stars.apps.registration.models import ValueDiscount
from stars.apps.notifications.models import EmailTemplate

# new imports
from stars.apps.tool.mixins import InstitutionAdminToolMixin
from stars.apps.helpers.mixins import ValidationMessageFormMixin
from stars.apps.helpers.queryset_sequence import QuerySetSequence

from django.views.generic import (CreateView, DeleteView, FormView, ListView,
                                  UpdateView)

logger = getLogger('stars.request')

def _get_current_institution(request):
    if hasattr(request.user, 'current_inst'):
        if not user_has_access_level(request.user, 'admin', request.user.current_inst):
            raise PermissionDenied('Sorry, only institution administrators have access.')
        return request.user.current_inst
    else:
        raise Http404


class ContactView(InstitutionAdminToolMixin, ValidationMessageFormMixin,
                  UpdateView):
    """
        Displays the contact form for an institution

        Contact form is customized based on the user's permission level
    """
    template_name = 'tool/manage/detail.html'

    def get_object(self):
        return self.get_institution()

    def get_form_class(self):
        if self.request.user.is_staff:
            FormClass = AdminInstitutionForm
        else:
            if self.get_institution().is_participant:
                FormClass = ParticipantContactForm
            else:
                FormClass = RespondentContactForm
        return FormClass


class InstitutionPaymentsView(InstitutionAdminToolMixin, ListView):
    """
        Displays a list of payments made by an institution.
    """
    context_object_name = 'payment_list'
    template_name = 'tool/manage/payments.html'

    def get_queryset(self):
        current_inst = self.get_institution()
        return SubscriptionPayment.objects.filter(
            subscription__institution=current_inst).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super(InstitutionPaymentsView, self).get_context_data(
            **kwargs)
        current_inst = self.get_institution()
        context['subscription_list'] = current_inst.subscription_set.all()
        context['current_inst'] = current_inst
        return context


class ResponsiblePartyListView(InstitutionAdminToolMixin, ListView):
    """
        Displays a list of responsible parties for an institution.
    """
    template_name = 'tool/manage/responsible_party_list.html'

    def get_queryset(self):
        current_inst = self.get_institution()
        return current_inst.responsibleparty_set.all()

    def get_context_data(self, **kwargs):
        context = super(ResponsiblePartyListView, self).get_context_data(
            **kwargs)
        context['tab_content_title'] = 'responsible parties'
        return context


class ResponsiblePartyEditView(InstitutionAdminToolMixin,
                               ValidationMessageFormMixin,
                               UpdateView):
    """
        Provides a form to edit a responsible party.
    """
    context_object_name = 'responsible_party'
    form_class = ResponsiblePartyForm
    model = ResponsibleParty
    success_url_name = 'responsible-party-list'
    template_name = 'tool/manage/responsible_party_edit.html'

    def get_context_data(self, **kwargs):
        context = super(ResponsiblePartyEditView, self).get_context_data(
            **kwargs)
        context['tab_content_title'] = 'edit a responsible party'
        context['credit_list'] = \
          self.get_object().get_creditusersubmissions().all()
        return context


class ResponsiblePartyDeleteView(InstitutionAdminToolMixin,
                                 ValidationMessageFormMixin,
                                 DeleteView):
    """
       Deletes a responsible party if they aren't tied to any submissions.
    """
    model = ResponsibleParty
    success_url_name = 'responsible-party-list'
    template_name = 'tool/manage/responsible_party_confirm_delete.html'

    def delete(self, *args, **kwargs):
        """
            Prevents this responsible party from being deleted if
            there are credits related to it.
        """
        responsible_party = self.get_object()
        if self.get_object().get_creditusersubmissions().count():
            messages.error(self.request,
                           "This Responsible Party cannot be removed because "
                           "he/she is listed with one or more credits.")
            return HttpResponseRedirect(
                reverse(
                    'responsible-party-list',
                    kwargs={ 'institution_slug': self.get_institution().slug }))

        else:
            messages.info(self.request,
                          "Successfully Deleted Responsible Party: %s" %
                          responsible_party)
            return super(ResponsiblePartyDeleteView, self).delete(*args,
                                                                  **kwargs)


class ResponsiblePartyCreateView(InstitutionAdminToolMixin,
                                 ValidationMessageFormMixin,
                                 CreateView):
    """
        Provides a form to create a responsible party.
    """
    form_class = ResponsiblePartyForm
    model = ResponsibleParty
    success_url_name = 'responsible-party-list'
    template_name = 'tool/manage/responsible_party_edit.html'
    valid_message = 'Responsible Party Added.'

    def get_context_data(self, **kwargs):
        context = super(ResponsiblePartyCreateView, self).get_context_data(
            **kwargs)
        context['tab_content_title'] = 'add a responsible party'
        return context

    def form_valid(self, form):
        """
            Attach the current institution to the responsible party before
            it's saved.
        """
        self.object = form.save(commit=False)
        self.object.institution = self.get_institution()
        self.object.save()
        return super(ResponsiblePartyCreateView, self).form_valid(form)


class AccountListView(InstitutionAdminToolMixin, ListView):
    """
        Displays a list of user accounts for an institution.
    """
    template_name = 'tool/manage/account_list.html'

    def get_queryset(self):
        institution = self.get_institution()
        stars_accounts = StarsAccount.objects.filter(institution=institution)
        pending_accounts = PendingAccount.objects.filter(institution=institution)
        return QuerySetSequence(stars_accounts, pending_accounts).order_by(
            'user.email')

    def get_context_data(self, **kwargs):
        context = super(AccountListView, self).get_context_data(**kwargs)
        context['tab_content_title'] = 'users'
        return context


class AccountCreateView(InstitutionAdminToolMixin, ValidationMessageFormMixin,
                        FormView):
    """
        Allows creation of StarsAccount (and PendingAccount) objects.

        If the email address provided doesn't match a StarsAccount,
        a PendingAccount is created instead.
    """
    form_class = AccountForm
    success_url_name = 'account-list'
    template_name = 'tool/manage/account_detail.html'
    valid_message = 'Account created.'

    def __init__(self, *args, **kwargs):
        """
            Declares new attributes; preferences and notify_form.
            Sure, this isn't necessary, but after they're declared
            here, they won't be a surprise when they're used later.
        """
        self.preferences = None
        self.notify_form = None
        super(AccountCreateView, self).__init__(*args, **kwargs)

    def get_aashe_user(self, email):
        """
            Returns the User object that ties together a STARS user account
            and an AASHE (Drupal) account.  If there's no matching AASHE
            account, None is returned.
        """
        user_list = xml_rpc.get_user_by_email(email)
        if user_list:
            return xml_rpc.get_user_from_user_dict(user_list[0], None)
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super(AccountCreateView, self).get_context_data(**kwargs)
        context['notify_form'] = self.notify_form
        context['tab_content_title'] = 'add a user'
        context['help_content_name'] = 'add_account'
        context['creating_new_account'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        """
            Save preferences for this institution, for use in form_valid()
            and get_context_data() later.
        """
        # self.kwargs is assigned in
        # django.views.generic.base.dispatch, which gets called at the
        # end of this method, but _update_preferences() below calls
        # get_institution(), which depends on self.kwargs already
        # being set.  That's why it gets set here first.
        self.kwargs = kwargs
        (self.preferences, self.notify_form) = _update_preferences(
            request, self.get_institution())
        return super(AccountCreateView, self).dispatch(
            request, *args, **kwargs)

    def form_valid(self, form):
        # Get the AASHE account info for this email
        user_level = form.cleaned_data['userlevel']
        user_email = form.cleaned_data['email']
        aashe_user = self.get_aashe_user(email=user_email)
        if aashe_user:
            StarsAccount.update_account(
                self.request.user,
                self.preferences.notify_users,
                self.get_institution(),
                user_level,
                user=aashe_user)
        else:
            messages.info(self.request,
                          "There is no AASHE user with e-mail: %s. "
                          "STARS Account is pending user's registration "
                          "at www.aashe.org." % user_email)
            PendingAccount.update_account(
                self.request.user,
                self.preferences.notify_users,
                self.get_institution(),
                user_level,
                user_email=user_email)
        return super(AccountCreateView, self).form_valid(form)


class AccountEditView(AccountCreateView):
    """
        Provides an edit view for StarsAccount and PendingAccount objects.
    """
    valid_message = 'User updated.'
    form_class = AccountForm

    def get_context_data(self, **kwargs):
        context = super(AccountEditView, self).get_context_data(
            **kwargs)
        context['tab_content_title'] = 'edit a user'
        context['help_content_name'] = 'edit_account'
        context['creating_new_account'] = False
        return context

    def get_initial(self):
        try:
            account = get_object_or_404(StarsAccount, id=self.kwargs['pk'])
        except Http404:
            account = get_object_or_404(PendingAccount, id=self.kwargs['pk'])
        return { 'userlevel': account.user_level,
                 'email': account.user.email }


class AccountDeleteView(InstitutionAdminToolMixin,
                        ValidationMessageFormMixin,
                        DeleteView):
    """
       Deletes a StarsAccount.
    """
    model = StarsAccount
    success_url_name = 'account-list'
    template_name = 'tool/manage/account_confirm_delete.html'

    def delete(self, request, *args, **kwargs):

        (preferences, notify_form) = _update_preferences(request,
                                                         self.get_institution())
        logger.info("Account: %s deleted." % self.get_object(),
                    extra={'request': request})
        if preferences.notify_users:
            self.get_object().notify(StarsAccount.DELETE_ACCOUNT, request.user,
                                     self.get_institution())
        return super(AccountDeleteView, self).delete(request, *args, **kwargs)


class PendingAccountDeleteView(AccountDeleteView):
    """
        Deletes a PendingAccount.
    """
    model = PendingAccount



class ShareDataView(InstitutionAdminToolMixin,
                    ValidationMessageFormMixin,
                    FormView):
    """
        Allows users to choose which third parties to share data with.
    """
    form_class = ThirdPartiesForm
    template_name = 'tool/manage/third_parties.html'

    def get_context_data(self, **kwargs):
        context = super(ShareDataView, self).get_context_data(**kwargs)
        context['tab_content_title'] = 'share data'
        context['help_content_name'] = 'edit_account'
        context['third_party_list'] = ThirdParty.objects.all()
        context['snapshot_list'] = SubmissionSet.objects.get_snapshots(
            self.get_institution())
        return context

##############################################################################
##############################################################################
##############################################################################
##############################################################################

def _update_preferences(request, institution):
    """
        Helper method to DRY code around managing institution preferences
        Returns (preferences, preferences_form)
    """
    try:
        preferences = institution.preferences
    except InstitutionPreferences.DoesNotExist:
        preferences = InstitutionPreferences(institution=institution)
    (notify_form,saved) = form_helpers.basic_save_form(
        request, preferences, '', NotifyUsersForm, show_message=False)
    return (preferences, notify_form)

def migrate_options(request, institution_slug=None):
    """
        Provides a tool to migrate a submission set
    """
    current_inst = _get_current_institution(request)
    current_submission = current_inst.current_submission
    latest_creditset = CreditSet.objects.get_latest()

    if current_inst.is_participant:
        available_submission_list = current_inst.submissionset_set.filter(status='r') | current_inst.submissionset_set.filter(status='f')
    else:
        available_submission_list = current_inst.submissionset_set.filter(status='r')

    template = 'tool/manage/migrate_submissionset.html'
    context = {
        "active_submission": current_submission,
        "latest_creditset": latest_creditset,
        "available_submission_list": available_submission_list,
    }
    return respond(request, template, context)

def migrate_data(request, ss_id):
    """
        Provides a tool to migrate a submission set
    """
    current_inst = _get_current_institution(request)
    current_submission = current_inst.current_submission
    old_submission = get_object_or_404(current_inst.submissionset_set.all(), id=ss_id)

    if not user_can_migrate_from_submission(request.user, old_submission):
        raise PermissionDenied("Sorry, but you don't have permission to migrate data.")

    ObjectForm = MigrateSubmissionSetForm

    object_form, saved = form_helpers.basic_save_form(request, current_submission, current_submission.id, ObjectForm)
    if saved:
        # start a migration task
        messages.info(request,
                      "Your migration is in progress. Please allow a "
                      "few minutes before you can access your submission.")
        perform_data_migration.delay(old_submission, request.user)
        return HttpResponseRedirect("/tool/")

    template = 'tool/manage/migrate_data.html'
    context = {
        "object_form": object_form,
        "active_submission": current_submission,
        "old_submission": old_submission,
    }
    return respond(request, template, context)

def migrate_version(request):
    """
        Provides a tool to migrate a submission set
    """
    current_inst = _get_current_institution(request)
    current_submission = current_inst.current_submission
    latest_creditset = CreditSet.objects.get_latest()

    if latest_creditset.version == current_submission.creditset.version:
        messages.error(request, "Already using %s." % latest_creditset)
        return HttpResponseRedirect("/tool/manage/migrate/")

    if not user_can_migrate_version(request.user, current_inst):
        raise PermissionDenied("Sorry, but you don't have permission "
                               "to migrate data.")

    ObjectForm = MigrateSubmissionSetForm

    object_form, saved = form_helpers.basic_save_form(request,
                                                      current_submission,
                                                      current_submission.id,
                                                      ObjectForm)
    if saved:
        # start a migration task
        messages.info(request, "Your migration is in progress. "
                      "Please allow a few minutes before you can access "
                      "your submission.")
        perform_migration.delay(current_submission,
                                latest_creditset,
                                request.user)
        return HttpResponseRedirect("/tool/")

    template = 'tool/manage/migrate_version.html'
    context = {
        "object_form": object_form,
        "current_submission": current_submission,
        "latest_creditset": latest_creditset,
    }
    return respond(request, template, context)

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


def send_exec_renew_email(institution):

    mail_to = [institution.executive_contact_email,]
    et = EmailTemplate.objects.get(slug="reg_renewal_exec")
    et.send_email(mail_to, {'institution': institution,})

@user_has_tool
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

    if current_inst.subscription_set.all():
        if is_member:
            reason = "member_renew"
        else:
            reason = "nonmember_renew"
    else:
        if is_member:
            reason = "member_reg"
        else:
            reason = "nonmember_reg"

    # calculate start date of subscription
    start_date = current_inst.get_last_subscription_end()
    if start_date and start_date > date.today():
        start_date += timedelta(days=1)
    else:
        start_date = date.today()

    pay_form = PaymentForm()
    later_form = PayLaterForm()

    if request.method == "POST":

        later_form = PayLaterForm(request.POST)
        if later_form.is_valid() and later_form.cleaned_data['confirm']:

            sub = Subscription(
                institution=current_inst,
                start_date=start_date,
                end_date=start_date + timedelta(SUBSCRIPTION_DURATION),
                amount_due=amount,
                paid_in_full=False,
                reason=reason)
            sub.save()

            if not current_inst.current_subscription:
                current_inst.current_subscription = sub
            current_inst.is_participant = True
            current_inst.save()

            if request.user.email != current_inst.contact_email:
                mail_to = [request.user.email, current_inst.contact_email]
            else:
                mail_to = [current_inst.contact_email,]

            if reason == "member_renew" or reason == "nonmember_renew":
                et = EmailTemplate.objects.get(slug="reg_renewal_unpaid")
            else:
                et = EmailTemplate.objects.get(slug="welcome_liaison_unpaid")

            email_context = {'institution': current_inst, 'amount': amount}
            et.send_email(mail_to, email_context)

            return HttpResponseRedirect("/tool/")
        else:
            pay_form = PaymentForm(request.POST)
            if pay_form.is_valid():
                payment_dict = get_payment_dict(pay_form, current_inst)
                if pay_form.cleaned_data['discount_code'] != None:
                        amount = _get_registration_price(
                            current_inst,
                            discount_code=pay_form.cleaned_data['discount_code'])
                        messages.info(request, "Discount Code Applied")
                product_dict = {
                    'price': amount,
                    'quantity': 1,
                    'name': "STARS Subscription Purchase",
                }

                result = process_payment(payment_dict, [product_dict],
                                         invoice_num=current_inst.aashe_id)
                if result.has_key('cleared') and result.has_key('msg'):
                    if result['cleared'] and result['trans_id']:

                        sub = Subscription(
                            institution=current_inst,
                            start_date=start_date,
                            end_date=(start_date +
                                      timedelta(SUBSCRIPTION_DURATION)),
                            amount_due=0,
                            paid_in_full=True,
                            reason=reason)
                        sub.save()

                        p = SubscriptionPayment(
                                        subscription=sub,
                                        date=datetime.now(),
                                        amount=amount,
                                        user=request.user,
                                        method='credit',
                                        confirmation=str(result['trans_id']),
                                    )
                        p.save()

                        if request.user.email != current_inst.contact_email:
                            mail_to = [request.user.email,
                                       current_inst.contact_email]
                        else:
                            mail_to = [current_inst.contact_email,]

                        if (reason == "member_renew" or
                            reason == "nonmember_renew"):
                            et = EmailTemplate.objects.get(
                                slug="reg_renewed_paid")
                            send_exec_renew_email(current_inst)
                        else:
                            et = EmailTemplate.objects.get(
                                slug="welcome_liaison_paid")

                        email_context = {'payment_dict': payment_dict,
                                         'institution': current_inst,
                                         "payment": p}
                        et.send_email(mail_to, email_context)

                        current_inst.current_subscription = sub
                        current_inst.is_participant = True
                        current_inst.save()

                        return HttpResponseRedirect("/tool/")
                    else:
                        messages.error(request, "Processing Error: %s" %
                                       result['msg'])
            else:
                messages.error(request, "Please correct the errors below")

    template = 'tool/manage/purchase_subscription.html'
    context = {
        "pay_form": pay_form,
        "later_form": later_form,
        "amount": amount,
        'is_member': is_member,
        'discount': discount,
    }
    return respond(request, template, context)

@user_has_tool
def pay_subscription(request, subscription_id):
    """
        Provides a view to allow institutions to pay for a subscription
    """
    current_inst = _get_current_institution(request)

    subscription = get_object_or_404(current_inst.subscription_set.all(),
                                     pk=subscription_id)
    amount = subscription.amount_due
    pay_form = PaymentForm()

    if request.method == "POST":
        pay_form = PaymentForm(request.POST)
        if pay_form.is_valid():
            payment_dict = get_payment_dict(pay_form, current_inst)
            if pay_form.cleaned_data['discount_code'] != None:
                # we know this exists because it was validated in the form
                discount = ValueDiscount.objects.get(
                    code=pay_form.cleaned_data['discount_code']).amount
                amount = amount - discount
                messages.info(request, "Discount Code Applied")
            product_dict = {
                'price': amount,
                'quantity': 1,
                'name': "STARS Subscription Payment",
            }

            result = process_payment(payment_dict, [product_dict],
                                     invoice_num=current_inst.aashe_id)
            if result.has_key('cleared') and result.has_key('msg'):
                if result['cleared'] and result['trans_id']:

                    subscription.amount_due = 0
                    subscription.paid_in_full = True
                    subscription.save()

                    p = SubscriptionPayment(
                                    subscription=subscription,
                                    date=datetime.now(),
                                    amount=amount,
                                    user=request.user,
                                    method='credit',
                                    confirmation=str(result['trans_id']),
                                )
                    p.save()

                    return HttpResponseRedirect("/tool/")
                else:
                    messages.error(request,
                                   "Processing Error: %s" % result['msg'])
        else:
            messages.error(request, "Please correct the errors below")

    template = 'tool/manage/pay_subscription.html'
    context = {
        "pay_form": pay_form,
        "amount": amount,
        'is_member': current_inst.is_member,
    }
    return respond(request, template, context)

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
