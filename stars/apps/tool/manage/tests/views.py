"""Tests for apps/tool/manage/views.py.
"""
from logging import getLogger, CRITICAL

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import TimeoutException
import testfixtures

import logical_rules
from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import (PendingAccount, StarsAccount,
                                            Subscription, SubscriptionPayment)
from stars.apps.institutions.tests.subscription import (GOOD_CREDIT_CARD,
                                                        BAD_CREDIT_CARD)
from stars.apps.payments.simple_credit_card import CreditCardProcessingError
from stars.apps.submissions.models import ResponsibleParty
from stars.apps.tests.live_server import StarsLiveServerTest
from stars.apps.tool.manage import views
from stars.apps.tool.tests.views import (InstitutionAdminToolMixinTest,
                                         InstitutionViewOnlyToolMixinTest)
from stars.test_factories import (CreditUserSubmissionFactory,
                                  PendingAccountFactory,
                                  ResponsiblePartyFactory,
                                  SubscriptionFactory,
                                  SubmissionSetFactory,
                                  StarsAccountFactory,
                                  UserFactory,
                                  ValueDiscountFactory)
# Don't bother me:
logger = getLogger('stars')
logger.setLevel(CRITICAL)


class ContactViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ContactView


class InstitutionPaymentsViewTest(InstitutionAdminToolMixinTest):

    view_class = views.InstitutionPaymentsView


class ResponsiblePartyListViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyListView


class ResponsiblePartyCreateViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyCreateView

    def test_post_creates_a_responsible_party(self):
        """Does a POST by an admin create a responsible party?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        responsible_party_count_before = ResponsibleParty.objects.count()
        new_responsible_party = ResponsiblePartyFactory.build(
            institution=self.institution)
        form_input = {'first_name': new_responsible_party.first_name,
                      'last_name': new_responsible_party.last_name,
                      'title': new_responsible_party.title,
                      'department': new_responsible_party.department,
                      'email': new_responsible_party.email,
                      'phone': new_responsible_party.phone}
        self.request.POST = form_input
        self.request.FILES = None
        _ = views.ResponsiblePartyCreateView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(responsible_party_count_before + 1,
                         ResponsibleParty.objects.count())

    def test_post_incomplete_form_does_not_create_a_responsible_party(self):
        """Does POSTing an incomplete form create a responsible party?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        responsible_party_count_before = ResponsibleParty.objects.count()
        new_responsible_party = ResponsiblePartyFactory.build(
            institution=self.institution)
        form_input = {'first_name': '',
                      'last_name': new_responsible_party.last_name,
                      'title': new_responsible_party.title,
                      'department': new_responsible_party.department,
                      'email': new_responsible_party.email,
                      'phone': new_responsible_party.phone}
        self.request.POST = form_input
        self.request.FILES = None
        _ = views.ResponsiblePartyCreateView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(responsible_party_count_before,
                         ResponsibleParty.objects.count())


class ResponsiblePartyEditViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyEditView

    def setUp(self):
        super(ResponsiblePartyEditViewTest, self).setUp()
        self.responsible_party = ResponsiblePartyFactory(
            institution=self.institution)

    def _get_pk(self):
        return self.responsible_party.id


class ResponsiblePartyDeleteViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyDeleteView

    def setUp(self):
        super(ResponsiblePartyDeleteViewTest, self).setUp()
        self.responsible_party = ResponsiblePartyFactory(
            institution=self.institution)

    def _get_pk(self):
        return self.responsible_party.id

    def test_delete_responsible_party_listed_with_no_credits(self):
        """Does delete for a resp. party listed with no credits succeed?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        responsible_party_count_before = ResponsibleParty.objects.count()
        self.request.POST = {}
        self.request.FILES = None
        _ = views.ResponsiblePartyDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.responsible_party.id)
        self.assertEqual(responsible_party_count_before - 1,
                         ResponsibleParty.objects.count())

    def test_delete_responsible_party_listed_with_credits(self):
        """Is delete for a responsible party listed with credits blocked?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = {}
        self.request.FILES = None
        self._make_credits_for_responsible_party()
        responsible_party_count_before = ResponsibleParty.objects.count()
        _ = views.ResponsiblePartyDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.responsible_party.id)
        self.assertEqual(responsible_party_count_before,
                         ResponsibleParty.objects.count())

    def test_delete_responsible_party_success_message(self):
        """Is a success message shown when all is ok?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = {}
        self.request.FILES = None
        _ = views.ResponsiblePartyDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.responsible_party.id)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('uccessfully Deleted' in info_message_divs[0].text)

    def test_delete_responsible_party_with_credits_error_message(self):
        """Is an error shown when a deletion fails?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = {}
        self.request.FILES = None
        self._make_credits_for_responsible_party()
        _ = views.ResponsiblePartyDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.responsible_party.id)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('cannot be removed' in info_message_divs[0].text)

    def _make_credits_for_responsible_party(self):
        """List some credits for this responsible_party."""
        credits = list()
        for credit in xrange(4):
            credits.append(CreditUserSubmissionFactory(
                responsible_party=self.responsible_party))


class AccountListViewTest(InstitutionAdminToolMixinTest):

    view_class = views.AccountListView

    def setUp(self):
        super(InstitutionAdminToolMixinTest, self).setUp()
        self.account.user_level = 'admin'
        self.account.save()

    def test_lists_stars_and_pending_accounts(self):
        """Are both StarsAccounts and PendingAccounts listed?"""
        accounts = [self.account]
        for i in xrange(4):
            accounts.append(StarsAccountFactory(institution=self.institution))

        pending_accounts = list()
        for account in accounts:
            pending_accounts.append(
                PendingAccountFactory(institution=self.institution))

        view = views.AccountListView.as_view()(
            self.request,
            institution_slug=self.institution.slug)
        soup = BeautifulSoup(view.rendered_content)
        table = soup.find('table')
        tbody = table.findChild('tbody')
        rows = tbody.findChildren('tr')
        self.assertEqual(len(rows), len(accounts) + len(pending_accounts))

    def test_sorting(self):
        """Are accounts sorted correctly (by email address)?"""
        def make_account(pending, email):
            if pending:
                return PendingAccountFactory(user_email=email,
                                             institution=self.institution)
            else:
                return StarsAccountFactory(user=UserFactory(email=email),
                                           institution=self.institution)

        def get_email(account):
            try:
                return account.user.email
            except KeyError:
                return account.user_email

        accounts = [make_account(pending=False, email='m@sa.com'),
                    make_account(pending=True, email='f@pa.com'),
                    make_account(pending=False, email='b@sa.com'),
                    make_account(pending=True, email='a@pa.com'),
                    make_account(pending=False, email='z@sa.com'),
                    make_account(pending=True, email='b@pa.com'),
                    self.account]

        view = views.AccountListView.as_view()(
            self.request,
            institution_slug=self.institution.slug)
        soup = BeautifulSoup(view.rendered_content)
        table = soup.find('table')
        tbody = table.findChild('tbody')

        email_tds = tbody.findChildren('td',
                                       {'class': 'account-email-address'})

        account_emails_on_page = [
            email_td.text.split()[0].strip() for email_td in email_tds
        ]

        self.assertListEqual(account_emails_on_page,
                             sorted([get_email(acct) for acct in accounts]))


class AccountCreateViewTest(InstitutionAdminToolMixinTest):

    view_class = views.AccountCreateView

    def test_form_valid_no_aashe_user_account_creates_pendingaccount(self):
        """Does form_valid() create a PendingAccount if no ASSHE acct exists?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        pending_account_count_before = PendingAccount.objects.count()
        form_input = {'email': 'joe.hump@fixityourself.com',
                      'userlevel': 'bystander'}
        self.request.POST = form_input
        _ = views.AccountCreateView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(pending_account_count_before + 1,
                         PendingAccount.objects.count())

    def test_form_valid_aashe_user_account_creates_starsaccount(self):
        """Does form_valid() create a StarsAccount if an ASSHE account exists?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        stars_account_count_before = StarsAccount.objects.count()
        form_input = {'email': 'joe.hump@fixityourself.com',
                      'userlevel': 'bystander'}
        self.request.POST = form_input
        with testfixtures.Replacer() as r:
            r.replace(
                'aashe.aasheauth.services.AASHEUserService.get_by_email',
                lambda s, e: [
                    {'replaced': 'replaced',
                     'mollom': {'session_id': 'replaced'}}
                ]
            )
            r.replace(
                'aashe.aasheauth.backends.AASHEBackend.'
                'get_user_from_user_dict',
                lambda x, y: UserFactory())
            _ = views.AccountCreateView.as_view()(
                request=self.request,
                institution_slug=self.institution.slug)
        self.assertEqual(stars_account_count_before + 1,
                         StarsAccount.objects.count())

#    def test_notify_user(self):
#        """Is a user notified when his account is created?"""
#        raise NotImplemented()


class AccountEditViewTest(InstitutionAdminToolMixinTest):

    view_class = views.AccountEditView

    def _get_pk(self):
        return self.account.id


class AccountDeleteViewTest(InstitutionAdminToolMixinTest):

    view_class = views.AccountDeleteView

    def _get_pk(self):
        return self.account.id

    def test_delete_stars_account(self):
        """Does deleting a stars account work?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        stars_account_count_before = StarsAccount.objects.count()
        self.request.POST = {}
        self.request.FILES = None
        _ = views.AccountDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.account.id)
        self.assertEqual(stars_account_count_before - 1,
                         StarsAccount.objects.count())

#    def test_notify_user(self):
#        """Is a user notified when his account is deleted?"""
#        raise NotImplemented()


class PendingAccountDeleteViewTest(InstitutionAdminToolMixinTest):

    view_class = views.PendingAccountDeleteView

    def setUp(self):
        super(PendingAccountDeleteViewTest, self).setUp()
        self.pending_account = PendingAccountFactory(
            institution=self.institution)

    def _get_pk(self):
        return self.pending_account.id

    def test_delete_stars_account(self):
        """Does deleting a pending account work?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        pending_account_count_before = PendingAccount.objects.count()
        self.request.POST = {}
        self.request.FILES = None
        _ = views.PendingAccountDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.pending_account.id)
        self.assertEqual(pending_account_count_before - 1,
                         PendingAccount.objects.count())


class ShareDataViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ShareDataView


class MigrateOptionsViewTest(InstitutionAdminToolMixinTest):

    view_class = views.MigrateOptionsView

    def setUp(self):
        super(MigrateOptionsViewTest, self).setUp()
        self.request.user.user_level = 'admin'
        self.r_status_submissionsets = list()
        self.f_status_submissionsets = list()
        for _ in xrange(2):
            self.r_status_submissionsets.append(SubmissionSetFactory(
                institution=self.institution, status='r'))
        for _ in xrange(2):
            self.f_status_submissionsets.append(SubmissionSetFactory(
                institution=self.institution, status='f'))

    def test__get_available_submissions_not_participant(self):
        self.institution.is_participant = False
        view = views.MigrateOptionsView
        available_submissions = view._get_available_submissions(
            institution=self.institution)
        self.assertEqual(len(available_submissions),
                         len(self.r_status_submissionsets) +
                         len(self.f_status_submissionsets))

    def test__get_available_submissions_is_participant(self):
        self.institution.is_participant = True
        view = views.MigrateOptionsView
        available_submissions = view._get_available_submissions(
            institution=self.institution)
        self.assertEqual(len(available_submissions),
                         len(self.r_status_submissionsets) +
                         len(self.f_status_submissionsets))


class MigrateViewTest(InstitutionAdminToolMixinTest):
    """
        A base class for MigrateDataViewTest and MigrateVersionViewTest.
    """
    view_class = None
    # Each subclass protects itself with a rule that must be True before
    # access is granted.  That's called 'gatekeeper_aashe_rule' here:
    gatekeeper_aashe_rule = None
    # Name of the function that actually starts the migration:
    migration_function_name = None

    def setUp(self):
        super(MigrateViewTest, self).setUp()
        self.institution.is_participant = True
        self.submissionset = SubmissionSetFactory(
            institution=self.institution, status='r')
        self.institution.current_submission = self.submissionset
        self.institution.save()

    def _get_pk(self):
        return self.submissionset.id

    def _stub_out_rule(self, rule_name, returns):
        """
            Deregisters a rule, and replaces it with a function that
            always returns arg named returns.
        """
        logical_rules.site.unregister(rule_name)
        logical_rules.site.register(rule_name,
                                    lambda *args: returns)

    def close_gate(self):
        super(MigrateViewTest, self).close_gate()
        self._stub_out_rule(rule_name=self.gatekeeper_aashe_rule,
                            returns=False)

    def open_gate(self):
        super(MigrateViewTest, self).open_gate()
        self._stub_out_rule(rule_name=self.gatekeeper_aashe_rule,
                            returns=True)

    def test_form_valid_starts_migration(self):
        """When all is ok, is a migration task started?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = {'is_locked': True}

        with testfixtures.Replacer() as r:
            self.open_gate()
            # stub out the migration function with a lambda that'll
            # raise a ZeroDivisionError, then we can check to
            # see if that error's raised when the migration
            # function should be called.
            r.replace('stars.apps.tool.manage.views.' +
                      self.migration_function_name,
                      lambda *args: 1/0)
            self.assertRaises(ZeroDivisionError,
                              self.view_class.as_view(),
                              self.request,
                              institution_slug=self.institution.slug,
                              pk=self._get_pk())


class MigrateDataViewTest(MigrateViewTest):

    view_class = views.MigrateDataView
    gatekeeper_aashe_rule = 'user_can_migrate_from_submission'
    migration_function_name = 'perform_data_migration.delay'


class MigrateVersionViewTest(MigrateViewTest):

    view_class = views.MigrateVersionView
    gatekeeper_aashe_rule = 'user_can_migrate_version'
    migration_function_name = 'perform_migration.delay'

    def test_dispatch_prevents_migration_when_already_at_latest_version(self):
        """Does dispatch prevent migration if current sub is at latest version?
        """
        self.account.user_level = 'admin'
        self.account.save()
        latest_creditset = CreditSet.objects.get_latest()
        self.submissionset.creditset = latest_creditset
        self.submissionset.save()
        try:
            _ = self.view_class().dispatch(
                self.request,
                institution_slug=self.institution.slug,
                pk=self._get_pk())
        except Exception, e:
            self.assertEqual(e.__class__.__name__, "PermissionDenied")

    def test_dispatch_allows_migration_when_not_already_at_latest_version(
            self):
        """Does dispatch allow migration if current sub isn't latest version?
        """
        self.account.user_level = 'admin'
        self.account.save()
        response = self.view_class().dispatch(
            self.request,
            institution_slug=self.institution.slug,
            pk=self._get_pk())
        self.assertEqual(response.status_code, 200)


class SubscriptionPriceViewTest(InstitutionViewOnlyToolMixinTest):

    view_class = views.SubscriptionPriceView

    def setUp(self):
        super(SubscriptionPriceViewTest, self).setUp()
        self.account.user_level = 'admin'
        self.account.save()
        self.PROMO_DISCOUNT_AMOUNT = 17
        self.promo_discount = ValueDiscountFactory(
            amount=self.PROMO_DISCOUNT_AMOUNT)

    def _get_view(self):
        return self.view_class.as_view()(
            self.request,
            institution_slug=self.institution.slug)

    def _get_soup(self, view=None):
        view = view or self._get_view()
        soup = BeautifulSoup(view.rendered_content)
        return soup

    def _get_amount_due_element(self, soup=None, view=None):
        soup = soup or self._get_soup(view)
        amount_due_element = soup.find(id="amount-due")
        return amount_due_element

    def _get_amount_due_text(self, soup=None, view=None):
        """Returns amount due as text."""
        amount_due_element = self._get_amount_due_element(soup=soup, view=view)
        return amount_due_element.text.strip()

    def _get_amount_due(self, soup=None, view=None):
        """Returns amount due as a float."""
        amount_due_text = self._get_amount_due_text(soup=soup, view=view)
        number_text = ''.join(
            (c for c in amount_due_text if (c.isdigit() or c in ['.', '-'])))
        amount_due_float = float(number_text)
        return amount_due_float

    def test_amount_due_gets_commas(self):
        """Does amount due show commas if > $999?"""
        self.institution.is_member = False  # no member discount
        self.institution.save()
        amount_due_text = self._get_amount_due_text()
        self.assertIn(',', amount_due_text)

    def test_amount_due_gets_dollar_sign(self):
        """Does amount due have a dollar sign in front of it?"""
        self.institution.is_member = False  # no member discount
        self.institution.save()
        amount_due_text = self._get_amount_due_text()
        self.assertIn('$', amount_due_text)

    def test_membership_discount_applied(self):
        """Is the membership discount applied?"""
        self.institution.is_member = False
        self.institution.save()
        amount_due_for_nonmember = self._get_amount_due()
        self.institution.is_member = True
        self.institution.save()
        amount_due_for_member = self._get_amount_due()
        self.assertLess(amount_due_for_member, amount_due_for_nonmember)

    def test_early_renewal_discount_applied(self):
        """Is the early renewal discount applied?"""
        amount_due_without_renewal_discount = self._get_amount_due()
        _ = SubscriptionFactory(institution=self.institution)
        amount_due_with_renewal_discount = self._get_amount_due()
        self.assertLess(amount_due_with_renewal_discount,
                        amount_due_without_renewal_discount)

    def test_submit_valid_promo_code_without_applying_it_first(self):
        """Does submitting the form w/a valid code w/o applying it work?

        I.e., if a valid code is entered, and the form is submitted
        without clicking the "Apply Promo Code" button, is the promo
        discount accepted?

        And by "accepted", I mean, is the promo code stashed in the
        request session, for the next view.
        """
        self.request.method = 'POST'
        self.request.POST = {'promo_code': self.promo_discount.code}
        _ = self._get_view()
        self.assertEqual(self.request.session['promo_code'],
                         self.promo_discount.code)

    def test_submit_invalid_promo_code_without_applying_it_first(self):
        """Does submitting the form w/an invalid code w/o applying it work?

        I.e., if an invalid code is entered, and the form is submitted
        without clicking the "Apply Promo Code" button, is the error
        displayed?
        """
        self.request.method = 'POST'
        self.request.POST = {'promo_code': 'BO-O-O-O-GUS!'}
        soup = self._get_soup()
        promo_code_element = soup.find(id='id_promo_code')
        parent = promo_code_element.find_parent()
        inline_helps = parent.findChildren(class_='help-inline')
        self.assertGreater(len(inline_helps), 0)


class SubscriptionPriceViewLiveServerTest(StarsLiveServerTest):

    def setUp(self):
        super(SubscriptionPriceViewLiveServerTest, self).setUp()
        self.promo_discount = ValueDiscountFactory(amount=37.50)
        self.go_to_reporting_tool()
        purchase_subscription_button = self.patiently_find(
            look_for='Purchase STARS Participant Subscription',
            by=By.LINK_TEXT)
        purchase_subscription_button.click()

    @property
    def promo_code_input(self):
        promo_code_input = self.patiently_find(look_for='id_promo_code',
                                               by=By.ID)
        return promo_code_input

    @property
    def amount_due_text(self):
        amount_due_element = self.patiently_find(look_for='amount-due',
                                                 by=By.ID)
        return amount_due_element.text

    @property
    def amount_due(self):
        text_without_commas_and_dollar_sign = ''.join(
            char for char in self.amount_due_text if char not in [',', '$'])
        amount_due_float = float(text_without_commas_and_dollar_sign)
        return amount_due_float

    @property
    def apply_promo_code_button(self):
        apply_promo_code_button = self.patiently_find(
            look_for='apply-promo-code-button', by=By.ID)
        return apply_promo_code_button

    def test_applying_valid_promo_code_updates_amount_due(self):
        """Does applying a valid promo code update the amount due?

        Where "applying ... promo code" means clicking the "Apply
        Promo Code" button.
        """
        initial_amount_due = self.amount_due

        self.promo_code_input.send_keys(self.promo_discount.code)

        self.apply_promo_code_button.click()

        discounted_amount_due = self.amount_due

        self.assertEqual(initial_amount_due,
                         discounted_amount_due + self.promo_discount.amount)

    def test_applying_invalid_promo_code_displays_field_error(self):
        """Does an invalid promo code display a field error messages?

        Where "applying ... promo code" means clicking the "Apply
        Promo Code" button.
        """
        self.promo_code_input.send_keys('BO-O-O-G-U-U-S!')

        self.apply_promo_code_button.click()

        error_div = self.patiently_find(look_for='error',
                                        by=By.CLASS_NAME)

        error_div_class = error_div.get_attribute('class')

        self.assertEqual(error_div_class,
                         'control-group error')

    def test_applying_invalid_promo_code_displays_alert(self):
        """Does an invalid promo code display an alert error message?

        Where "applying ... promo code" means clicking the "Apply
        Promo Code" button.
        """
        self.promo_code_input.send_keys('BO-O-O-G-U-U-S!')

        self.apply_promo_code_button.click()

        error_div = self.patiently_find(look_for='alert',
                                        by=By.CLASS_NAME)

        error_div_class = error_div.get_attribute('class')

        self.assertEqual(error_div_class,
                         'alert fade in alert-error')

    def test_applying_blank_promo_code_clears_field_errors(self):
        """Are field errors cleared by applying a blank promo code?

        Where "applying ... a promo code" means clicking the "Apply
        Promo Code" button.
        """
        self.promo_code_input.send_keys('BO-O-O-G-U-U-S!')

        self.apply_promo_code_button.click()

        # make sure there are some errors to clear:
        error_div = self.patiently_find(look_for='error',
                                        by=By.CLASS_NAME)
        error_div_class = error_div.get_attribute('class')
        self.assertEqual(error_div_class, 'control-group error')

        self.promo_code_input.clear()

        self.apply_promo_code_button.click()

        with self.assertRaises(TimeoutException):
            error_div = self.patiently_find(look_for='error',
                                            by=By.CLASS_NAME,
                                            wait_for=1)

    def test_applying_blank_promo_code_clears_alerts(self):
        """Are alert messages cleared by applying a blank promo code?

        Where "applying ... a promo code" means clicking the "Apply
        Promo Code" button.
        """
        self.promo_code_input.send_keys('BO-O-O-G-U-U-S!')

        self.apply_promo_code_button.click()

        # make sure there are some errors to clear:
        error_div = self.patiently_find(look_for='alert',
                                        by=By.CLASS_NAME)
        error_div_class = error_div.get_attribute('class')
        self.assertEqual(error_div_class,
                         'alert fade in alert-error')

        self.promo_code_input.clear()

        self.apply_promo_code_button.click()

        with self.assertRaises(TimeoutException):
            error_div = self.patiently_find(look_for='alert',
                                            by=By.CLASS_NAME,
                                            wait_for=1)

    def test_amount_due_gets_commas_after_applying_discount(self):
        """Does amount due show commas if > $999 after applying discount?"""
        self.promo_code_input.send_keys(self.promo_discount.code)

        self.apply_promo_code_button.click()

        discounted_amount_due_text = self.amount_due_text

        self.assertIn(',', discounted_amount_due_text)

    def test_amount_due_gets_dollar_sign_after_applying_discount(self):
        """Does amount due have a dollar sign in front of it after discount?
        """
        self.promo_code_input.send_keys(self.promo_discount.code)

        self.apply_promo_code_button.click()

        discounted_amount_due_text = self.amount_due_text

        self.assertIn('$', discounted_amount_due_text)


class SubscriptionPaymentOptionsViewTest(InstitutionViewOnlyToolMixinTest):

    view_class = views.SubscriptionPaymentOptionsView

    def setUp(self):
        super(SubscriptionPaymentOptionsViewTest, self).setUp()
        self.request.session['promo_code'] = ''
        self.request.session['amount_due'] = 1400

    def test_free_subscription_bypasses_payment_forms(self):
        """Are the payment forms skipped for 100% discounted subs?
        Payment forms include the 'payment options' and 'enter your
        credit card info' forms."""
        promo_discount = ValueDiscountFactory(amount=0,
                                              percentage=100)

        self.request.session['promo_code'] = promo_discount.code

        response = self.view_class.as_view()(
            self.request,
            institution_slug=self.institution.slug)

        self.assertEquals(response.get('Location'),
                          reverse('subscription-create',
                                  args=[self.institution.slug]))


class SubscriptionCreateViewTest(InstitutionViewOnlyToolMixinTest):

    fixtures = ['email_templates.json']

    view_class = views.SubscriptionCreateView

    def setUp(self):
        super(SubscriptionCreateViewTest, self).setUp()
        self.request.session['promo_code'] = ''
        self.request.session['amount_due'] = 1400
        self.request.session[views.PAY_WHEN] = Subscription.PAY_NOW

    def test_pay_later_creates_subscription(self):
        """Is a subscription created when user wants to pay later?"""

        self.request.session[views.PAY_WHEN] = Subscription.PAY_LATER
        self.request.method = 'POST'

        initial_subscription_count = Subscription.objects.count()

        self.open_gate()
        _ = self.view_class.as_view()(request=self.request,
                                      institution_slug=self.institution.slug)

        self.assertEqual(Subscription.objects.count(),
                         initial_subscription_count + 1)

    def test_pay_now_creates_subscription(self):
        """Is a subscription created when user wants to pay now?"""

        self.request.method = 'POST'
        self.request.POST = {'card_number': GOOD_CREDIT_CARD,
                             'exp_month': '12',
                             'exp_year': '2022'}

        initial_subscription_count = Subscription.objects.count()

        self.open_gate()
        _ = self.view_class.as_view()(request=self.request,
                                      institution_slug=self.institution.slug)

        self.assertEqual(Subscription.objects.count(),
                         initial_subscription_count + 1)

    def test_pay_now_creates_payment(self):
        """Is a payment created when a user wants to pay now?"""

        self.request.method = 'POST'
        self.request.POST = {'card_number': GOOD_CREDIT_CARD,
                             'exp_month': '12',
                             'exp_year': '2022'}

        initial_payment_count = SubscriptionPayment.objects.count()
        self.open_gate()
        _ = self.view_class.as_view()(request=self.request,
                                      institution_slug=self.institution.slug)

        self.assertEqual(SubscriptionPayment.objects.count(),
                         initial_payment_count + 1)

    def test_subscription_created_when_purchase_error(self):
        """Is a subscription *not* created when there's a purchase error?"""

        self.request.method = 'POST'
        self.request.POST = {'card_number': BAD_CREDIT_CARD,
                             'exp_month': '12',
                             'exp_year': '2022'}

        initial_subscription_count = Subscription.objects.count()
        self.open_gate()
        _ = self.view_class.as_view()(request=self.request,
                                      institution_slug=self.institution.slug)

        self.assertEqual(Subscription.objects.count(),
                         initial_subscription_count)


class SubscriptionPaymentCreateViewTest(InstitutionViewOnlyToolMixinTest):

    view_class = views.SubscriptionPaymentCreateView

    def setUp(self):
        """Depends on Subscription.create()."""
        super(SubscriptionPaymentCreateViewTest, self).setUp()
        # self.request.session[views.PAY_WHEN] = Subscription.PAY_LATER
        self.subscription = Subscription.create(institution=self.institution)
        self.subscription.save()

    def _get_pk(self):
        return self.subscription.id

    def test_form_valid_creates_payment(self):
        """Does form_valid() create a payment?"""
        self.account.user_level = self.blessed_user_level
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = {'card_number': GOOD_CREDIT_CARD,
                             'exp_month': '10',
                             'exp_year': '2020'}

        initial_payment_count = SubscriptionPayment.objects.count()

        _ = self.view_class.as_view()(request=self.request,
                                      institution_slug=self.institution.slug,
                                      pk=self.subscription.id)

        self.assertEqual(SubscriptionPayment.objects.count(),
                         initial_payment_count + 1)

    def test_form_valid_no_payment_created_when_purchase_error(self):
        """Does form_valid *not* create a payment if there's a purchase error?
        """
        self.account.user_level = self.blessed_user_level
        self.account.save()
        self.request.session[views.PAY_WHEN] = Subscription.PAY_NOW
        self.request.method = 'POST'
        self.request.POST = {'card_number': BAD_CREDIT_CARD,
                             'exp_month': '10',
                             'exp_year': '2020'}

        initial_payment_count = SubscriptionPayment.objects.count()

        with self.assertRaises(CreditCardProcessingError):
            _ = self.view_class.as_view()(
                request=self.request,
                institution_slug=self.institution.slug,
                pk=self.subscription.id)

        self.assertEqual(SubscriptionPayment.objects.count(),
                         initial_payment_count)
