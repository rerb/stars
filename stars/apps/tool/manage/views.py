from logging import getLogger

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import (CreateView, DeleteView, FormView, ListView,
                                  TemplateView, UpdateView)

from aashe.aasheauth.services import AASHEUserService
from aashe.aasheauth.backends import AASHEBackend

# from stars.apps.accounts import xml_rpc
from stars.apps.credits.models import CreditSet
from stars.apps.helpers.forms import form_helpers
from stars.apps.helpers.mixins import ValidationMessageFormMixin
from stars.apps.helpers.queryset_sequence import QuerySetSequence
from stars.apps.institutions.models import (StarsAccount, Subscription,
                                            SubscriptionPayment,
                                            SubscriptionPurchaseError,
                                            PendingAccount)
from stars.apps.institutions.models import Institution
from stars.apps.payments import credit_card
from stars.apps.tool.manage.forms import (PayNowForm,
                                          PaymentOptionsForm, PayLaterForm)
from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.tasks import (perform_migration,
                                          perform_data_migration)
from stars.apps.third_parties.models import ThirdParty
from stars.apps.tool.manage.forms import (AccountForm, AdminInstitutionForm,
                                          InstitutionPreferences,
                                          MigrateSubmissionSetForm,
                                          NotifyUsersForm,
                                          ParticipantContactForm,
                                          RespondentContactForm,
                                          ResponsibleParty,
                                          ResponsiblePartyForm,
                                          ThirdPartiesForm)
from stars.apps.tool.mixins import (InstitutionAdminToolMixin,
                                    InstitutionToolMixin)

logger = getLogger('stars.request')

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


class ContactView(InstitutionAdminToolMixin, ValidationMessageFormMixin,
                  UpdateView):
    """
        Displays the contact form for an institution

        Contact form is customized based on the user's permission level
    """
    tab_content_title = 'contact'
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
    tab_content_title = 'payments'
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
    tab_content_title = 'responsible parties'
    template_name = 'tool/manage/responsible_party_list.html'

    def get_queryset(self):
        current_inst = self.get_institution()
        return current_inst.responsibleparty_set.all()


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
    tab_content_title = 'edit a responsible party'
    template_name = 'tool/manage/responsible_party_edit.html'

    def get_context_data(self, **kwargs):
        context = super(ResponsiblePartyEditView, self).get_context_data(
            **kwargs)
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
    tab_content_title = 'delete a responsible party'
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
    tab_content_title = 'add a responsible party'
    template_name = 'tool/manage/responsible_party_edit.html'
    valid_message = 'Responsible Party Added.'

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
    tab_content_title = 'users'
    template_name = 'tool/manage/account_list.html'

    def get_queryset(self):
        institution = self.get_institution()
        stars_accounts = StarsAccount.objects.filter(institution=institution)
        pending_accounts = PendingAccount.objects.filter(institution=institution)
        return QuerySetSequence(stars_accounts, pending_accounts).order_by(
            'user.email')


class AccountCreateView(InstitutionAdminToolMixin, ValidationMessageFormMixin,
                        FormView):
    """
        Allows creation of StarsAccount (and PendingAccount) objects.

        If the email address provided doesn't match a StarsAccount,
        a PendingAccount is created instead.
    """
    form_class = AccountForm
    success_url_name = 'account-list'
    tab_content_title = 'add a user'
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
        service = AASHEUserService()
        backend = AASHEBackend()
        user_list = service.get_by_email(email)
        if user_list:
            # a hack to make these compatible
            user_dict = {'user': user_list[0],
                         'sessid': "no-session-key"}
            return backend.get_user_from_user_dict(user_dict)
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super(AccountCreateView, self).get_context_data(**kwargs)
        context['notify_form'] = self.notify_form
        context['help_content_name'] = 'add_account'
        context['creating_new_account'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        """
            Save preferences for this institution, for use in form_valid()
            and get_context_data() later.
        """
        (self.preferences, self.notify_form) = _update_preferences(
            request, Institution.objects.get(slug=kwargs['institution_slug']))
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
            self.valid_message = ''  # So no "Account created." message shows.
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
    form_class = AccountForm
    tab_content_title = 'edit a user'
    valid_message = 'User updated.'

    def get_context_data(self, **kwargs):
        context = super(AccountEditView, self).get_context_data(
            **kwargs)
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
    tab_content_title = 'delete a user'
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
                    TemplateView):
    """
        Users can view their snapshots
    """
    tab_content_title = 'share data'
    template_name = 'tool/manage/share_snapshots.html'

    def get_context_data(self, **kwargs):
        context = super(ShareDataView, self).get_context_data(**kwargs)
        context['third_party_sharing_list'] = self.get_institution().third_parties.all()
        context['snapshot_list'] = SubmissionSet.objects.get_snapshots(
                                                        self.get_institution())
        return context


class ShareThirdPartiesView(InstitutionAdminToolMixin,
                            ValidationMessageFormMixin,
                            UpdateView):
    """
        Users chose which third parties to share data with
    """
    form_class = ThirdPartiesForm
    model = Institution
    tab_content_title = 'share data'
    template_name = 'tool/manage/share_third_parties.html'

    def get_context_data(self, **kwargs):
        context = super(ShareThirdPartiesView, self).get_context_data(**kwargs)
        context['help_content_name'] = 'edit_account'
        context['third_party_list'] = ThirdParty.objects.all()
        context['snapshot_count'] = SubmissionSet.objects.get_snapshots(
            self.get_institution()).count()
        return context

    def get_object(self):
        return self.get_institution()

#    def form_valid(self, form):
#        form.save()
#        return super(ShareThirdPartiesView, self).form_valid(form)


class MigrateOptionsView(InstitutionAdminToolMixin, TemplateView):
    """
        Provides a user with migration options (i.e., migrate some data or
        migrate a submission).
    """
    tab_content_title = 'migrate'
    template_name = 'tool/manage/migrate_submissionset.html'

    def get_context_data(self, **kwargs):
        context = super(MigrateOptionsView, self).get_context_data(**kwargs)
        context['active_submission'] = self.get_institution().current_submission
        context['latest_creditset'] = CreditSet.objects.get_latest()
        context['available_submission_list'] = self._get_available_submissions(
            institution=self.get_institution())
        return context

    @classmethod
    def _get_available_submissions(cls, institution):
        submissions = (institution.submissionset_set.filter(status='r') |
                    institution.submissionset_set.filter(status='f'))
        return submissions


class MigrateDataView(InstitutionAdminToolMixin,
                      ValidationMessageFormMixin,
                      UpdateView):
    """
        Provides a form to solicit user's confirmation that this
        data migration should proceed.
    """
    form_class = MigrateSubmissionSetForm
    model = SubmissionSet
    success_url_name = 'tool-summary'
    tab_content_title = 'data migration'
    template_name = 'tool/manage/migrate_data.html'
    valid_message = ("Your migration is in progress. Please allow a "
                     "few minutes before you can access your submission.")
    invalid_message = ("Before the migration can begin, you need to "
                       "confirm your intention by checking that little "
                       "check box down there above the Migrate My Data "
                       "button.")

    def update_logical_rules(self):
        super(MigrateDataView, self).update_logical_rules()
        self.add_logical_rule({ 'name': 'user_can_migrate_from_submission',
                                'param_callbacks': [
                                    ('user', 'get_request_user'),
                                    ('submission', '_get_old_submission')] })

    def _get_old_submission(self):
        return get_object_or_404(
            self.get_institution().submissionset_set.all(),
            id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(MigrateDataView, self).get_context_data(**kwargs)
        context['active_submission'] = self.get_institution().current_submission
        context['old_submission'] = self._get_old_submission()
        return context

    def form_valid(self, form):
        # if user hasn't checked the magic box:
        if not form.cleaned_data['is_locked']:
            return self.form_invalid(form)
        # otherwise, start a migration task
        perform_data_migration.delay(self._get_old_submission(),
                                     self.request.user)
        return super(MigrateDataView, self).form_valid(form)


class MigrateVersionView(InstitutionAdminToolMixin,
                         ValidationMessageFormMixin,
                         UpdateView):
    """
        Provides a form to solicit user's confirmation that this
        version migration should proceed.
    """
    form_class = MigrateSubmissionSetForm
    model = SubmissionSet
    success_url_name = 'migrate-options'
    template_name = 'tool/manage/migrate_version.html'
    tab_content_title = 'migrate version'
    valid_message = ("Your migration is in progress. Please allow a "
                     "few minutes before you can access your submission.")
    invalid_message = ("Before the migration can begin, you need to "
                       "confirm your intention by checking that little "
                       "check box down there above the Migrate My Data "
                       "button.")

    def update_logical_rules(self):
        super(MigrateVersionView, self).update_logical_rules()
        self.add_logical_rule({ 'name': 'user_can_migrate_version',
                                'param_callbacks': [
                                    ('user', 'get_request_user'),
                                    ('current_inst', 'get_institution')] })


    def get_context_data(self, **kwargs):
        context = super(MigrateVersionView, self).get_context_data(**kwargs)
        current_submission = self.get_institution().current_submission
        context['current_submission'] = current_submission
        context['latest_creditset'] = CreditSet.objects.get_latest()
        return context

    def form_valid(self, form):
        # if user hasn't checked the magic box, do not proceed . . .
        if not form.cleaned_data['is_locked']:
            return self.form_invalid(form)
        # . . . otherwise, start a migration task
        perform_migration.delay(self.get_institution().current_submission,
                                CreditSet.objects.get_latest(),
                                self.request.user)
        return super(MigrateVersionView, self).form_valid(form)


PAY_WHEN = 'pay_when'


class SubscriptionPaymentOptionsView(InstitutionToolMixin,
                                     ValidationMessageFormMixin,
                                     FormView):
    """
        Provides a form by which a user's preference to pay now
        (by credit card) or pay later (after being billed) for a
        new subscription can be specified.

        Redirects to the view that creates a Subscription.
    """
    form_class = PaymentOptionsForm
    success_url_name = 'subscription-create'
    tab_content_title = 'purchase a subscription: payment options'
    template_name = 'tool/manage/subscription_payment_options.html'
    valid_message = ''  # Only want to use invalid_message.
    invalid_message = 'Please choose to pay now or pay later.'

    def update_logical_rules(self):
        super(SubscriptionPaymentOptionsView, self).update_logical_rules()
        self.add_logical_rule({ 'name': 'user_has_view_access',
                                'param_callbacks': [
                                    ('user', 'get_request_user'),
                                    ('institution', 'get_institution')] })

    def get_context_data(self, **kwargs):
        context = super(SubscriptionPaymentOptionsView,
                        self).get_context_data(**kwargs)
        (subscription_start_date, subscription_end_date) = (
            Subscription.get_date_range_for_new_subscription(
                self.get_institution()))
        context['subscription_start_date'] = subscription_start_date
        context['subscription_end_date'] = subscription_end_date
        return context

    def form_valid(self, form):
        # Pass the payment option selected on:
        self.request.session[PAY_WHEN] = form.cleaned_data[PAY_WHEN]
        return super(SubscriptionPaymentOptionsView, self).form_valid(form)


class SubscriptionPaymentCreateBaseView(ValidationMessageFormMixin,
                                        InstitutionToolMixin,
                                        FormView):
    """
        Provides a common base for the views that accept credit
        card payments for subscriptions.
    """
    success_url_name = 'tool-summary'

    def update_logical_rules(self):
        super(SubscriptionPaymentCreateBaseView, self).update_logical_rules()
        self.add_logical_rule({ 'name': 'user_has_view_access',
                                'param_callbacks': [
                                    ('user', 'get_request_user'),
                                    ('institution', 'get_institution')] })

    def get_context_data(self, **kwargs):
        context = super(SubscriptionPaymentCreateBaseView,
                        self).get_context_data(**kwargs)
        context['breadcrumb'] = 'purchase subscription'
        return context


class SubscriptionCreateView(SubscriptionPaymentCreateBaseView):
    """
        Creates a Subscription.

        If self.request.session['PAY_WHEN'] == Subscription.PAY_NOW,
        the form displayed requests credit card info, and an attempt to
        charge the card is made.

        If self.request.session['PAY_WHEN'] = Subscription.PAY_LATER,
        the form displayed requests only a promo code.

        After creating a Subscription, it's purchased, which, if paying
        now, will trigger a credit card transaction.
    """
    success_url_name = 'tool-summary'
    template_name = 'tool/manage/subscription_payment_create.html'

    @property
    def pay_when(self):
        if not getattr(self, '_pay_when', False):
            self._pay_when = self.request.session[PAY_WHEN]
        return self._pay_when

    def form_valid(self, form):
        """
            Creates a Subscription, and then purchases it.
        """
        self.subscription, promo_code_applied = Subscription.create(
            institution=self.get_institution(),
            promo_code=form.cleaned_data['promo_code'])

        if promo_code_applied:
            messages.info(self.request, "Promo code discount applied!")

        # must save subscription before trying to pay it; it's got to have
        # an id for SubscriptionPayment.subscription_id:
        self.subscription.save()

        try:
            self.subscription.purchase(pay_when=self.pay_when,
                                       user=self.request.user,
                                       form=form)
        except SubscriptionPurchaseError as spe:
            messages.error(self.request, str(spe))
            return self.form_invalid(form)


        del self.request.session[PAY_WHEN]

        return super(SubscriptionCreateView, self).form_valid(form)

    def form_invalid(self, form):
        """
            If a Subscription was created in form_valid(), this
            deletes it.
        """
        if hasattr(self, 'subscription'):
            if self.subscription.id:
                self.subscription.delete()
        return super(SubscriptionCreateView, self).form_invalid(form)

    def get_form_class(self):
        return { Subscription.PAY_LATER: PayLaterForm,
                 Subscription.PAY_NOW: PayNowForm }[self.pay_when]

    def get_tab_content_title(self):
        return { Subscription.PAY_LATER: 'purchase a subscription: pay later',
                 Subscription.PAY_NOW: 'purchase a subscription: pay now' }[
                     self.pay_when]

    def get_valid_message(self):
        return """Thank you!
                  Your new subscription lasts from
                  {start} to {finish}.""".format(
                      start=self.subscription.start_date,
                      finish=self.subscription.end_date)


class SubscriptionPaymentCreateView(SubscriptionPaymentCreateBaseView):
    """
        Allows user to make a credit card payment toward a
        subscription.  Accepts full amount due only (no partial
        payments).
    """
    form_class = PayNowForm
    success_url_name = 'tool-summary'
    template_name = 'tool/manage/subscription_payment_create.html'
    valid_message = 'Thank you! Your payment has been processed.'

    @property
    def subscription(self):
        """
            There's some tight coupling here with urls.py.
            We're pulling the subscription id out of self.kwargs,
            so if, say, that parameter is renamed in urls.py, this
            will break.
        """
        self._subscription = Subscription.objects.get(pk=self.kwargs['pk'])
        return self._subscription

    def form_valid(self, form):
        try:
            self.subscription.pay(amount=self.subscription.amount_due,
                                  user=self.request.user,
                                  form=form)
        except credit_card.CreditCardProcessingError as ccpe:
            messages.error(self.request, str(ccpe))
            return self.form_invalid(form)

        return super(SubscriptionPaymentCreateView, self).form_valid(form)

    def get_tab_content_title(self):
        return 'pay now; amount due: ${0:.2f}'.format(
            self.subscription.amount_due)
