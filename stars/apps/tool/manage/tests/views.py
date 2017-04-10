"""Tests for apps/tool/manage/views.py.
"""
import time
from logging import getLogger, CRITICAL

import logical_rules
import testfixtures
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django_membersuite_auth.models import MemberSuitePortalUser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import TimeoutException

from stars.apps import payments
from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import (PendingAccount, StarsAccount,
                                            Subscription, SubscriptionPayment,
                                            Institution)
from stars.apps.institutions.tests.subscription import (GOOD_CREDIT_CARD,
                                                        BAD_CREDIT_CARD)
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
        views.ResponsiblePartyCreateView.as_view()(
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
        views.ResponsiblePartyCreateView.as_view()(
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
        views.ResponsiblePartyDeleteView.as_view()(
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
        views.ResponsiblePartyDeleteView.as_view()(
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
        views.ResponsiblePartyDeleteView.as_view()(
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
        views.ResponsiblePartyDeleteView.as_view()(
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

    def test_form_valid_no_msportaluser_account_creates_pendingaccount(self):
        """Does form_valid() create a PendingAccount if no MS acct exists?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        pending_account_count_before = PendingAccount.objects.count()
        form_input = {'email': 'joe.hump@fixityourself.com',
                      'userlevel': 'bystr'}
        self.request.POST = form_input
        views.AccountCreateView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(pending_account_count_before + 1,
                         PendingAccount.objects.count())

    def test_form_valid_creates_starsaccount(self):
        """Does form_valid() create a StarsAccount?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        MemberSuitePortalUser.objects.create(
            email="joe.hump@fixityourself.com")
        stars_account_count_before = StarsAccount.objects.count()
        form_input = {'email': 'joe.hump@fixityourself.com',
                      'userlevel': 'bystr'}
        self.request.POST = form_input
        views.AccountCreateView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(stars_account_count_before + 1,
                         StarsAccount.objects.count())


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
        views.AccountDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.account.id)
        self.assertEqual(stars_account_count_before - 1,
                         StarsAccount.objects.count())


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
        views.PendingAccountDeleteView.as_view()(
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
    # Name of the task that actually starts the migration:
    migration_task_name = None

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


        class migrationTask(object):
            def delay(self, *args, **kwargs):
                return 1 / 0

        with testfixtures.Replacer() as r:
            self.open_gate()
            # stub out the migration function with a lambda that'll
            # raise a ZeroDivisionError, then we can check to
            # see if that error's raised when the migration
            # function should be called.
            r.replace('stars.apps.tool.manage.views.' +
                      self.migration_task_name,
                      migrationTask())
            self.assertRaises(ZeroDivisionError,
                              self.view_class.as_view(),
                              self.request,
                              institution_slug=self.institution.slug,
                              pk=self._get_pk())


class MigrateDataViewTest(MigrateViewTest):

    view_class = views.MigrateDataView
    gatekeeper_aashe_rule = 'user_can_migrate_from_submission'
    migration_task_name = 'perform_data_migration'


class MigrateVersionViewTest(MigrateViewTest):

    view_class = views.MigrateVersionView
    gatekeeper_aashe_rule = 'user_can_migrate_version'
    migration_task_name = 'perform_migration'

    def test_dispatch_prevents_migration_when_already_at_latest_version(self):
        """Does dispatch prevent migration if current sub is at latest version?
        """
        self.account.user_level = 'admin'
        self.account.save()
        latest_creditset = CreditSet.objects.get_latest()
        self.submissionset.creditset = latest_creditset
        self.submissionset.save()
        try:
            self.view_class().dispatch(
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


class SubscriptionCreateWizardLiveServerTest(StarsLiveServerTest):

    fixtures = ['notification_emailtemplate_tests.json']

    def setUp(self):
        super(SubscriptionCreateWizardLiveServerTest, self).setUp()
        self.promo_discount = ValueDiscountFactory(amount=37.50)

    @property
    def purchase_subscription_button(self):
        purchase_subscription_button = self.patiently_find(
            look_for='Purchase STARS Full Access Subscription',
            by=By.LINK_TEXT)
        return purchase_subscription_button

    @property
    def promo_code_input(self):
        promo_code_input = self.patiently_find(look_for='promo_code',
                                               by=By.CLASS_NAME)
        return promo_code_input

    @property
    def amount_due_text(self):
        """Returns amount due as text."""
        amount_due_element = self.patiently_find(look_for='amount-due',
                                                 by=By.ID)
        return amount_due_element.text

    @property
    def amount_due(self):
        """Returns amount due as a number."""
        text_without_commas_and_dollar_sign = ''.join(
            char for char in self.amount_due_text if char not in [',', '$'])
        amount_due_float = float(text_without_commas_and_dollar_sign)
        return amount_due_float

    @property
    def apply_promo_code_button(self):
        """Returns the Apply Promo Code button."""
        apply_promo_code_button = self.patiently_find(
            look_for='apply-promo-code-button', by=By.ID)
        return apply_promo_code_button

    @property
    def next_button(self):
        """Returns the Next button."""
        buttons = self.selenium.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == 'Next':
                return button
        raise Exception('no Next button?')

    @property
    def final_purchase_subscription_button(self):
        """Returns the final Purchase Subscription button."""
        buttons = self.selenium.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == 'Purchase Subscription':
                return button
        raise Exception('no Purchase Subscription button?')

    def click_purchase_subscription_button(self):
        self.go_to_reporting_tool()
        self.purchase_subscription_button.click()

    def test_amount_due_gets_commas(self):
        """Does amount due show commas if > $999?"""
        self.institution.is_member = False  # no member discount
        self.institution.save()
        self.click_purchase_subscription_button()
        self.assertIn(',', self.amount_due_text)

    def test_amount_due_gets_dollar_sign(self):
        """Does amount due have a dollar sign in front of it?"""
        self.click_purchase_subscription_button()
        self.assertEqual('$', self.amount_due_text[0])

    def test_membership_discount_applied(self):
        """Is the membership discount applied?"""
        self.institution.is_member = False
        self.institution.save()
        self.click_purchase_subscription_button()
        amount_due_for_nonmember = self.amount_due
        self.institution.is_member = True
        self.institution.save()
        self.click_purchase_subscription_button()
        amount_due_for_member = self.amount_due
        self.assertLess(amount_due_for_member, amount_due_for_nonmember)

    def test_early_renewal_discount_applied(self):
        """Is the early renewal discount applied?"""
        self.click_purchase_subscription_button()
        amount_due_without_renewal_discount = self.amount_due
        SubscriptionFactory(institution=self.institution)
        self.click_purchase_subscription_button()
        amount_due_with_renewal_discount = self.amount_due
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
        self.click_purchase_subscription_button()
        initial_amount_due = self.amount_due
        self.promo_code_input.send_keys(self.promo_discount.code)
        self.next_button.click()
        discounted_amount_due = self.amount_due  # from payment options page
        self.assertEqual(initial_amount_due - self.promo_discount.amount,
                         discounted_amount_due)

    def test_submit_invalid_promo_code_without_applying_it_first(self):
        """Does submitting the form w/an invalid code w/o applying it work?

        I.e., if an invalid code is entered, and the form is submitted
        without clicking the "Apply Promo Code" button, is the error
        displayed?
        """
        self.click_purchase_subscription_button()
        self.promo_code_input.send_keys('BO-O-O-O-GUS!')
        self.next_button.click()
        inline_error = self.patiently_find(look_for='help-inline',
                                           by=By.CLASS_NAME)
        self.assertEqual(inline_error.text,
                         'BO-O-O-O-GUS! is not a valid discount code')

    def test_applying_valid_promo_code_updates_amount_due(self):
        """Does applying a valid promo code update the amount due?

        Where "applying ... promo code" means clicking the "Apply
        Promo Code" button.
        """
        self.click_purchase_subscription_button()

        initial_amount_due = self.amount_due

        self.promo_code_input.send_keys(self.promo_discount.code)

        self.apply_promo_code_button.click()

        time.sleep(1)
        discounted_amount_due = self.amount_due

        self.assertEqual(initial_amount_due,
                         discounted_amount_due + self.promo_discount.amount)

    def test_applying_invalid_promo_code_displays_field_error(self):
        """Does an invalid promo code display a field error messages?

        Where "applying ... promo code" means clicking the "Apply
        Promo Code" button.
        """
        self.click_purchase_subscription_button()

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
        self.click_purchase_subscription_button()

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
        self.click_purchase_subscription_button()

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
                                            timeout=1)

    def test_applying_blank_promo_code_clears_alerts(self):
        """Are alert messages cleared by applying a blank promo code?

        Where "applying ... a promo code" means clicking the "Apply
        Promo Code" button.
        """
        self.click_purchase_subscription_button()

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
                                            timeout=1)

    def test_amount_due_gets_commas_after_applying_discount(self):
        """Does amount due show commas if > $999 after applying discount?"""
        self.click_purchase_subscription_button()

        self.promo_code_input.send_keys(self.promo_discount.code)

        self.apply_promo_code_button.click()

        discounted_amount_due_text = self.amount_due_text

        self.assertIn(',', discounted_amount_due_text)

    def test_amount_due_gets_dollar_sign_after_applying_discount(self):
        """Does amount due have a dollar sign in front of it after discount?
        """
        self.click_purchase_subscription_button()

        self.promo_code_input.send_keys(self.promo_discount.code)

        self.apply_promo_code_button.click()

        discounted_amount_due_text = self.amount_due_text

        self.assertIn('$', discounted_amount_due_text)

    def test_free_subscription_bypasses_payment_forms(self):
        """Are the payment forms skipped for 100% discounted subs?
        Payment forms include the 'payment options' and 'enter your
        credit card info' forms."""
        generous_discount = ValueDiscountFactory(amount=0,
                                                 percentage=100)

        self.click_purchase_subscription_button()

        self.promo_code_input.send_keys(generous_discount.code)

        self.apply_promo_code_button.click()

        self.next_button.click()

        # Should forward to the final form, with a Purchase Subscription
        # button on it:

        self.assertIsNotNone(self.final_purchase_subscription_button)

    @property
    def payment_options_radio_buttons(self):
        """Returns the payment options radio buttons."""
        input_buttons = self.selenium.find_elements_by_tag_name('input')
        radio_buttons = [ib for ib in input_buttons
                         if ib.get_attribute('type') == 'radio']
        return radio_buttons

    @property
    def pay_now_radio_button(self):
        """Returns the radio button that indicates 'Pay now please'."""
        for radio_button in self.payment_options_radio_buttons:
            if radio_button.get_attribute('value') == Subscription.PAY_NOW:
                return radio_button
        raise Exception('no Pay Now radio button?')

    @property
    def pay_later_radio_button(self):
        """Returns the radio button that indicates 'Pay later please'."""
        for radio_button in self.payment_options_radio_buttons:
            if radio_button.get_attribute('value') == Subscription.PAY_LATER:
                return radio_button
        raise Exception('no Pay Later radio button?')

    def get_credit_card_element(self, end_of_id):
        text_input_elements = self.get_input_elements(type="text")
        for text_input_element in text_input_elements:
            if text_input_element.get_attribute("id").endswith(end_of_id):
                return text_input_element
        raise Exception("no {0} element?".format(end_of_id.replace("_",
                                                                   " ")))

    @property
    def credit_card_number_element(self):
        credit_card_number_element = self.get_credit_card_element(
            "card_number")
        return credit_card_number_element

    @property
    def credit_card_expiration_month_element(self):
        credit_card_expiration_month_element = self.get_credit_card_element(
            "exp_month")
        return credit_card_expiration_month_element

    @property
    def credit_card_expiration_year_element(self):
        credit_card_expiration_year_element = self.get_credit_card_element(
            "exp_year")
        return credit_card_expiration_year_element

    @property
    def credit_card_cvv_element(self):
        credit_card_cvv_element = self.get_credit_card_element("cvv")
        return credit_card_cvv_element

    @property
    def credit_card_number(self):
        return self.credit_card_number_element.text

    @credit_card_number.setter
    def credit_card_number(self, value):
        self.credit_card_number_element.clear()
        self.credit_card_number_element.send_keys(value)

    @property
    def credit_card_expiration_month(self):
        return self.credit_card_expiration_month_element.text

    @credit_card_expiration_month.setter
    def credit_card_expiration_month(self, value):
        self.credit_card_expiration_month_element.clear()
        self.credit_card_expiration_month_element.send_keys(value)

    @property
    def credit_card_expiration_year(self):
        return self.credit_card_expiration_year_element.text

    @credit_card_expiration_year.setter
    def credit_card_expiration_year(self, value):
        self.credit_card_expiration_year_element.clear()
        self.credit_card_expiration_year_element.send_keys(value)

    @property
    def credit_card_cvv(self):
        return self.credit_card_cvv_element.text

    @credit_card_cvv.setter
    def credit_card_cvv(self, value):
        self.credit_card_cvv_element.clear()
        self.credit_card_cvv_element.send_keys(value)

    # def wait(self, tag_name="body"):
    #     # Wait until the response is received
    #     WebDriverWait(SELENIUM, timeout).until(
    #         lambda driver: driver.find_element_by_tag_name(tag_name))

    def get_input_elements(self, type):
        input_elements = self.selenium.find_elements_by_tag_name('input')
        type_elements = [ib for ib in input_elements
                         if ib.get_attribute("type") == type]
        return type_elements

    def test_pay_later_creates_subscription(self):
        """Is a subscription created when user wants to pay later?"""
        subs_before = Subscription.objects.count()
        self.click_purchase_subscription_button()
        self.next_button.click()
        self.pay_later_radio_button.click()
        self.next_button.click()
        self.final_purchase_subscription_button.click()
        subs_after = Subscription.objects.count()
        self.assertEqual(subs_before + 1, subs_after)

    def purchase_and_pay_now(self, credit_card_number=GOOD_CREDIT_CARD):
        """Go through the subscription process, and pay for it now."""
        self.click_purchase_subscription_button()
        self.next_button.click()
        # Payment options form:
        self.pay_now_radio_button.click()
        self.next_button.click()
        # Credit card info form:
        self.credit_card_number = credit_card_number
        self.credit_card_expiration_month = "12"
        self.credit_card_expiration_year = "2020"
        self.credit_card_cvv = "123"
        self.final_purchase_subscription_button.click()

    def test_pay_now_creates_subscription(self):
        """Is a subscription created when user wants to pay now?"""
        subscriptions_before = Subscription.objects.count()
        self.purchase_and_pay_now()
        subscriptions_after = Subscription.objects.count()
        self.assertEqual(subscriptions_before + 1, subscriptions_after)

    def test_pay_now_creates_payment(self):
        """Is a payment created when a user wants to pay now?"""
        payments_before = SubscriptionPayment.objects.count()
        self.purchase_and_pay_now()
        payments_after = SubscriptionPayment.objects.count()
        self.assertEqual(payments_before + 1, payments_after)

    def test_subscription_is_not_created_when_purchase_error(self):
        """Is a subscription *not* created when there's a purchase error?"""
        subscriptions_before = Subscription.objects.count()
        self.purchase_and_pay_now(credit_card_number=BAD_CREDIT_CARD)
        subscriptions_after = Subscription.objects.count()
        self.assertEqual(subscriptions_before, subscriptions_after)

    def test_payment_is_not_created_when_purchase_error(self):
        """Is a payment *not* created when there's a purchase error?"""
        payments_before = SubscriptionPayment.objects.count()
        self.purchase_and_pay_now(credit_card_number=BAD_CREDIT_CARD)
        payments_after = SubscriptionPayment.objects.count()
        self.assertEqual(payments_before, payments_after)


class SubscriptionPaymentCreateViewTest(InstitutionViewOnlyToolMixinTest):

    view_class = views.SubscriptionPaymentCreateView

    def setUp(self):
        """Depends on Subscription.create()."""
        super(SubscriptionPaymentCreateViewTest, self).setUp()
        self.subscription = Subscription.create(institution=self.institution)
        self.subscription.save()
        # make this the current subscription
        self.institution.current_subscription = self.subscription
        self.institution.save()

    def _get_pk(self):
        return self.subscription.id

    def test_form_valid_creates_payment(self):
        # confirm that the institution isn't marked as a participant
        i = Institution.objects.get(pk=1)
        self.assertFalse(i.is_participant)

        """Does form_valid() create a payment?"""
        self.account.user_level = self.blessed_user_level
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = {'card_number': GOOD_CREDIT_CARD,
                             'exp_month': '10',
                             'exp_year': '2020',
                             'cvv': '123'}

        initial_payment_count = SubscriptionPayment.objects.count()

        self.view_class.as_view()(request=self.request,
                                      institution_slug=self.institution.slug,
                                      pk=self.subscription.id)

        self.assertEqual(SubscriptionPayment.objects.count(),
                         initial_payment_count + 1)

        # confirm institution is now a participant
        i = Institution.objects.get(pk=1)
        self.assertTrue(i.is_participant)

    def test_form_valid_no_payment_created_when_purchase_error(self):
        """Does form_valid *not* create a payment if there's a purchase error?
        """
        self.account.user_level = self.blessed_user_level
        self.account.save()
        self.request.session[payments.views.PAY_WHEN] = Subscription.PAY_NOW
        self.request.method = 'POST'
        self.request.POST = {'card_number': BAD_CREDIT_CARD,
                             'exp_month': '10',
                             'exp_year': '2020',
                             'cvv': '123'}

        initial_payment_count = SubscriptionPayment.objects.count()

        self.view_class.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.subscription.id)

        self.assertEqual(SubscriptionPayment.objects.count(),
                         initial_payment_count)
