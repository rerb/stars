"""Tests for apps/tool/manage/views.py.
"""
from logging import getLogger, CRITICAL
import sys
if sys.version < '2.7':
    from django.utils import unittest
else:
    import unittest

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.shortcuts import render
from django.test import TestCase
from django.test.client import Client, RequestFactory
import testfixtures

import aashe_rules
from stars.test_factories import (CreditUserSubmissionFactory,
     InstitutionFactory, PendingAccountFactory, ResponsiblePartyFactory,
     SubmissionSetFactory, StarsAccountFactory, UserFactory)
from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import (PendingAccount, StarsAccount,
                                            Subscription, SubscriptionPayment)
from stars.apps.institutions.tests.subscription import (get_pay_now_form_data,
                                                        GOOD_CREDIT_CARD,
                                                        BAD_CREDIT_CARD)
from stars.apps.submissions.models import ResponsibleParty
from stars.apps.tool.manage import views

# Don't bother me:
logger = getLogger('stars')
logger.setLevel(CRITICAL)


def _get_request_ready_for_messages():
    """
        Returns a request ready to handle messages.
    """
    def apply_message_middleware(request):
        request = apply_session_middleware(request)
        MessageMiddleware().process_request(request)
        return request

    def apply_session_middleware(request):
        SessionMiddleware().process_request(request)
        return request

    request = HttpRequest()
    request = apply_message_middleware(request)
    return request

def _make_credits_for_responsible_party(responsible_party):
    """List some credits with a responsible_party."""
    credits = list()
    for credit in xrange(4):
        credits.append(
            CreditUserSubmissionFactory(responsible_party=responsible_party))
    return credits


class _InstitutionToolMixinTest(TestCase):
    """
        Provides a base TestCase that checks if a view;

            1. is GET-able by users; specify a user_level if
               the view is protected by user_level;

            2. if the view is protected by a user_level, is it
               *not* GET-able by a user w/o that user_level;

            3. returns a loadable (optionally, only by a user with
               a specified user_level) success_url.
    """
    view_class = None  # Must be set in subclass.
    blocked_user_level = None  # user_level that should be blocked
    blessed_user_level = None  # user_level that should be allowed to GET

    def setUp(self):
        self.institution = InstitutionFactory(slug='on-the-beach-soldier')

        self.account = StarsAccountFactory(institution=self.institution)

        self.request = _get_request_ready_for_messages()
        self.request.user = self.account.user
        self.request.method = 'GET'

    def _get_pk(self):
        """
            Provides the value for the kwarg named 'pk' that's
            passed to the view's on_view() product.  Subclasses
            might need to override this, if, for instance, the
            view under test expects the id of a ResponsibleParty
            as the value of the pk kwarg.
        """
        pass

    def test_get_succeeds(self, user_level=''):
        """Is view.as_view() GET-able?

            Simple test to see if self.view_class.as_view()
            is GET-able.
        """
        self.account.user_level = user_level or self.blessed_user_level
        self.account.save()
        response = self.view_class.as_view()(
            self.request,
            institution_slug=self.institution.slug,
            pk=self._get_pk())
        self.assertEqual(response.status_code, 200)

    def test_get_is_blocked(self, user_level=''):
        """Is view_class.as_view() blocked by user_level?

           Test to see if self.view_class.as_view() is *not*
           is GET-able by a user without the appropriate user_level.

           If a view has no user_level protection, pass None as user_level
           and this test will be skipped.
        """
        if user_level is None:
            return unittest.skip('no user_level specified')
        self.account.user_level = self.blocked_user_level or ''
        self.account.save()
        response = self.view_class.as_view()(
            self.request,
            institution_slug=self.institution.slug,
            pk=self._get_pk())
        self.assertEqual(response.status_code, 403)

    def test_success_url_is_loadable(self, user_level=''):
        """Is the url returned by get_success_url() loadable?

           If the success url is protected by a user_level check,
           specify that in the user_level argument.
        """
        self.account.user_level = user_level or self.blessed_user_level
        self.account.save()
        view = self.view_class()
        # Hack a request object onto the view, since it'll be
        # referenced if no success_url or success_url_name is specified
        # in the view:
        view.request = RequestFactory()
        # Now set request.path to a sentinel value we can watch for:
        view.request.path = 'SENTINEL'
        success_url = view.get_success_url(
            institution_slug=self.institution.slug)
        if success_url is not 'SENTINEL':
            response = Client().get(success_url, follow=True)
            self.assertEqual(response.status_code, 200)


class _InstitutionAdminToolMixinTest(_InstitutionToolMixinTest):
    """
        Provides a base TestCase that checks if a view;

            1. is non GET-able by non-admin users;

            2. is GET-able by admin users, and;

            3. returns a loadable (by an admin) success_url.
    """

    view_class = None  # Must be set in subclass.
    blocked_user_level = ''
    blessed_user_level = 'admin'


class InstitutionPaymentsViewTest(_InstitutionAdminToolMixinTest):

    view_class = views.InstitutionPaymentsView


class ResponsiblePartyListViewTest(_InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyListView


class ResponsiblePartyCreateViewTest(_InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyCreateView

    def test_post_creates_a_responsible_party(self):
        """Does a POST by an admin create a responsible party?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        responsible_party_count_before = ResponsibleParty.objects.count()
        new_responsible_party = ResponsiblePartyFactory.build(
            institution=self.institution)
        form_input = { 'first_name': new_responsible_party.first_name,
                       'last_name': new_responsible_party.last_name,
                       'title': new_responsible_party.title,
                       'department': new_responsible_party.department,
                       'email': new_responsible_party.email,
                       'phone': new_responsible_party.phone }
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
        form_input = { 'first_name': '',
                       'last_name': new_responsible_party.last_name,
                       'title': new_responsible_party.title,
                       'department': new_responsible_party.department,
                       'email': new_responsible_party.email,
                       'phone': new_responsible_party.phone }
        self.request.POST = form_input
        self.request.FILES = None
        _ = views.ResponsiblePartyCreateView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(responsible_party_count_before,
                         ResponsibleParty.objects.count())


class ResponsiblePartyEditViewTest(_InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyEditView

    def setUp(self):
        super(ResponsiblePartyEditViewTest, self).setUp()
        self.responsible_party = ResponsiblePartyFactory(
            institution=self.institution)

    def _get_pk(self):
        return self.responsible_party.id


class ResponsiblePartyDeleteViewTest(_InstitutionAdminToolMixinTest):

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
        _ = _make_credits_for_responsible_party(self.responsible_party)
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
        _ = _make_credits_for_responsible_party(self.responsible_party)
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


class AccountListViewTest(_InstitutionAdminToolMixinTest):

    view_class = views.AccountListView

    def test_lists_stars_and_pending_accounts(self):
        """Are both StarsAccounts and PendingAccounts listed?"""
        self.account.user_level = 'admin'
        self.account.save()

        accounts = list()
        for i in xrange(4):
            accounts.append(StarsAccountFactory(institution=self.institution))

        pending_accounts = list()
        for account in accounts:
            pending_accounts.append(
                PendingAccountFactory(institution=self.institution))

        _ = views.AccountListView.as_view()(
            self.request,
            institution_slug=self.institution.slug)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        table = soup.find('table')
        tbody = table.findChild('tbody')
        rows = tbody.findChildren('tr')
        self.assertEqual(len(rows), len(accounts) + len(pending_accounts))


class AccountCreateViewTest(_InstitutionAdminToolMixinTest):

    view_class = views.AccountCreateView

    def test_form_valid_no_aashe_user_account_creates_pendingaccount(self):
        """Does form_valid() create a PendingAccount if no ASSHE account exists?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        pending_account_count_before = PendingAccount.objects.count()
        form_input = { 'email': 'joe.hump@fixityourself.com',
                       'userlevel': 'bystander' }
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
        form_input = { 'email': 'joe.hump@fixityourself.com',
                       'userlevel': 'bystander' }
        self.request.POST = form_input
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.manage.views.xml_rpc.get_user_by_email',
                lambda x : ['replaced',])
            r.replace(
                'stars.apps.tool.manage.views.xml_rpc.get_user_from_user_dict',
                lambda x, y: UserFactory())
            _ = views.AccountCreateView.as_view()(
                request=self.request,
                institution_slug=self.institution.slug)
        self.assertEqual(stars_account_count_before + 1,
                         StarsAccount.objects.count())

    def test_notify_user(self):
        """Is a user notified when his account is created?"""
        raise NotImplemented()


class AccountEditViewTest(_InstitutionAdminToolMixinTest):

    view_class = views.AccountEditView

    def _get_pk(self):
        return self.account.id


class AccountDeleteViewTest(_InstitutionAdminToolMixinTest):

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

    def test_notify_user(self):
        """Is a user notified when his account is deleted?"""
        raise NotImplemented()


class PendingAccountDeleteViewTest(_InstitutionAdminToolMixinTest):

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


class ShareDataViewTest(_InstitutionAdminToolMixinTest):

    view_class = views.ShareDataView


class MigrateOptionsViewTest(_InstitutionAdminToolMixinTest):

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
                         len(self.r_status_submissionsets))

    def test__get_available_submissions_is_participant(self):
        self.institution.is_participant = True
        view = views.MigrateOptionsView
        available_submissions = view._get_available_submissions(
            institution=self.institution)
        self.assertEqual(len(available_submissions),
                         len(self.r_status_submissionsets) +
                         len(self.f_status_submissionsets))


class _MigrateDataVersionViewTest(_InstitutionAdminToolMixinTest):
    """
        A base class for MigrateDataViewTest and MigrateVersionViewTest.
    """

    # Name of the class to test:
    view_class = None
    # Each subclass protects itself with a rule that must be True before
    # access is granted.  That's called 'gatekeeper_rule' here:
    gatekeeper_rule = None
    # Name of the function that actually starts the migration:
    migration_function_name = None

    def setUp(self):
        super(_MigrateDataVersionViewTest, self).setUp()
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
        aashe_rules.site.unregister(rule_name)
        aashe_rules.site.register(rule_name,
                                  lambda *args: returns)

    def close_gate(self):
        """
            Tweaks the gatekeeper rule to prevent access.
        """
        self._stub_out_rule(rule_name=self.gatekeeper_rule, returns=False)

    def open_gate(self):
        """
            Tweaks the gatekeeper rule to allow access.
        """
        self._stub_out_rule(rule_name=self.gatekeeper_rule, returns=True)

    def test_get_by_non_priveleged_user(self):
        """Does a GET by a user w/o the appropriate priveleges fail?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.close_gate()
        response = self.view_class.as_view()(
            self.request,
            institution_slug=self.institution.slug,
            pk=self._get_pk())
        self.assertEqual(response.status_code, 403)

    def test_get_by_priveleged_user(self):
        """Does a GET by a user w/the appropriate priveleges succeed?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.open_gate()
        response = self.view_class.as_view()(
            self.request,
            institution_slug=self.institution.slug,
            pk=self._get_pk())
        self.assertEqual(response.status_code, 200)

    def test_form_valid_starts_migration(self):
        """When all is ok, is a migration task started?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = { 'is_locked': True }

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


class MigrateDataViewTest(_MigrateDataVersionViewTest):

    view_class = views.MigrateDataView
    gatekeeper_rule = 'user_can_migrate_from_submission'
    migration_function_name = 'perform_data_migration.delay'


class MigrateVersionViewTest(_MigrateDataVersionViewTest):

    view_class = views.MigrateVersionView
    gatekeeper_rule = 'user_can_migrate_version'
    migration_function_name = 'perform_migration.delay'

    def test_dispatch_prevents_migration_when_already_at_latest_version(self):
        """Does dispatch prevent migration if current sub is at latest version?
        """
        self.account.user_level = 'admin'
        self.account.save()
        latest_creditset = CreditSet.objects.get_latest()
        self.submissionset.creditset = latest_creditset
        self.submissionset.save()
        response = self.view_class().dispatch(
            self.request,
            institution_slug=self.institution.slug,
            pk=self._get_pk())
        self.assertEqual(response.status_code, 403)

    def test_dispatch_allows_migration_when_not_already_at_latest_version(self):
        """Does dispatch allow migration if current sub isn't at latest version?
        """
        self.account.user_level = 'admin'
        self.account.save()
        response = self.view_class().dispatch(
            self.request,
            institution_slug=self.institution.slug,
            pk=self._get_pk())
        self.assertEqual(response.status_code, 200)


class _InstitutionViewOnlyToolMixinTest(_InstitutionToolMixinTest):
    """
       Base class for InstitutionToolMixin views that are accessible
       by users with at least 'view' access for the institution.
    """
    blessed_user_level = 'view'
    blocked_user_level = ''


class SubscriptionPaymentOptionsViewTest(_InstitutionViewOnlyToolMixinTest):

    view_class = views.SubscriptionPaymentOptionsView


class SubscriptionCreateViewTest(_InstitutionViewOnlyToolMixinTest):

    fixtures = ['email_templates.json']

    view_class = views.SubscriptionCreateView

    def setUp(self):
        super(SubscriptionCreateViewTest, self).setUp()
        self.request.session[views.PAY_WHEN] = Subscription.PAY_LATER

    def test_form_valid_creates_subscription(self):
        """Does form_valid() create a subscription?"""
        institution = InstitutionFactory(slug='nancy-man')

        self.request.method = 'POST'
        self.request.POST = { 'promo_code': '' }

        initial_subscription_count = Subscription.objects.count()

        _ = self.view_class.as_view()(request=self.request,
                                      institution_slug=institution.slug)

        self.assertEqual(Subscription.objects.count(),
                         initial_subscription_count + 1)

    def test_form_valid_pay_now_creates_payment(self):
        """Does form_valid() create a payment when user is paying now?"""
        institution = InstitutionFactory(slug='fancy-man')

        self.request.session[views.PAY_WHEN] = Subscription.PAY_NOW
        self.request.method = 'POST'
        self.request.POST = get_pay_now_form_data(
            card_number=GOOD_CREDIT_CARD)

        initial_payment_count = SubscriptionPayment.objects.count()

        _ = self.view_class.as_view()(request=self.request,
                                      institution_slug=institution.slug)

        self.assertEqual(SubscriptionPayment.objects.count(),
                         initial_payment_count + 1)

    def test_form_valid_no_subrx_created_when_purchase_error(self):
        """Does form_valid() *not* create a subrx if there's a purchase error?
        """
        institution = InstitutionFactory(slug='fancy-man')

        self.request.session[views.PAY_WHEN] = Subscription.PAY_NOW
        self.request.method = 'POST'
        self.request.POST = get_pay_now_form_data(card_number=BAD_CREDIT_CARD)

        initial_subscription_count = Subscription.objects.count()

        _ = self.view_class.as_view()(request=self.request,
                                      institution_slug=institution.slug)

        self.assertEqual(Subscription.objects.count(),
                         initial_subscription_count)


class SubscriptionPaymentCreateViewTest(_InstitutionViewOnlyToolMixinTest):

    view_class = views.SubscriptionPaymentCreateView

    def setUp(self):
        """Depends on Subscription.create()."""
        super(SubscriptionPaymentCreateViewTest, self).setUp()
        # self.request.session[views.PAY_WHEN] = Subscription.PAY_LATER
        (self.subscription, _) = Subscription.create(
            institution=self.institution)
        self.subscription.save()

    def _get_pk(self):
        return self.subscription.id

    def test_form_valid_creates_payment(self):
        """Does form_valid() create a payment?"""
        self.account.user_level = self.blessed_user_level
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = get_pay_now_form_data(
            card_number=GOOD_CREDIT_CARD)

        initial_payment_count = SubscriptionPayment.objects.count()

        _ = self.view_class.as_view()(request=self.request,
                                      institution_slug=self.institution.slug,
                                      pk=self.subscription.id)

        self.assertEqual(SubscriptionPayment.objects.count(),
                         initial_payment_count + 1)

    def test_form_valid_no_payment_created_when_purchase_error(self):
        """Does form_valid() *not* create a payment if there's a purchase error?
        """
        self.account.user_level = self.blessed_user_level
        self.account.save()
        self.request.session[views.PAY_WHEN] = Subscription.PAY_NOW
        self.request.method = 'POST'
        self.request.POST = get_pay_now_form_data(card_number=BAD_CREDIT_CARD)

        initial_payment_count = SubscriptionPayment.objects.count()

        _ = self.view_class.as_view()(request=self.request,
                                      institution_slug=self.institution.slug,
                                      pk=self.subscription.id)

        self.assertEqual(SubscriptionPayment.objects.count(),
                         initial_payment_count)
