"""Tests for apps/tool/manage/views.py.
"""
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.shortcuts import render
from django.test import TestCase
from django.test.client import Client, RequestFactory
import testfixtures

from stars.test_factories import (CreditUserSubmissionFactory,
     InstitutionFactory, PendingAccountFactory, ResponsiblePartyFactory,
     SubmissionSetFactory, StarsAccountFactory, UserFactory)
from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import Institution, PendingAccount, \
     StarsAccount, Subscription
from stars.apps.registration.models import ValueDiscount
from stars.apps.submissions.models import ResponsibleParty, SubmissionSet
from stars.apps.tool.manage import views

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


class ViewsTest(TestCase):

    fixtures = ['responsible_party_test_data.json']

    def setUp(self):
        self.request = _get_request_ready_for_messages()

        self.request.user = User.objects.get(pk=1)
        self.request.institution = Institution.objects.get(pk=1)
        self.request.user.current_inst = self.request.institution
        self.request.user.has_perm = lambda x: True
        self.request.method = 'POST'

        self.subscription = Subscription(start_date='2000-01-01',
                                         end_date='3000-01-01',
                                         amount_due=500.00)
        self.subscription.institution = self.request.institution
        self.subscription.save()
        value_discount = ValueDiscount(
            code=MockPaymentForm().cleaned_data['discount_code'],
            amount=100.00, start_date='1000-01-01', end_date='5000-01-01')
        value_discount.save()

    def test_migrate_data_migration_started_message(self):
        """Does migrate_data show a message when a migration starts?
        """
        submissionset = SubmissionSet.objects.get(pk=1)
        self.request.institution.current_submission = submissionset
        self.request.institution.save()
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            r.replace(
                'stars.apps.tool.manage.views.user_can_migrate_from_submission',
                lambda x,y: True)
            r.replace(
                'stars.apps.tool.manage.views.form_helpers.basic_save_form',
                lambda w,x,y,z: (None, True))
            _ = views.migrate_data(self.request, 1)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('migration is in progress' in
                        info_message_divs[0].text)

    def test_migrate_version_already_using_version_error_message(self):
        """Does migrate_version show an error msg if that version is current?
        """
        submissionset = SubmissionSet.objects.get(pk=1)
        submissionset.creditset = CreditSet.objects.get_latest()
        submissionset.save()
        self.request.institution.current_submission = submissionset
        self.request.institution.save()
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            r.replace(
                'stars.apps.tool.manage.views.user_can_migrate_version',
                lambda x,y: True)
            _ = views.migrate_version(self.request)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('Already using' in error_message_divs[0].text)

    def test_migrate_version_migration_started_message(self):
        """Does migrate_version show a message when a migration starts?
        """
        submissionset = SubmissionSet.objects.get(pk=1)
        self.request.institution.current_submission = submissionset
        self.request.institution.save()
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            r.replace(
                'stars.apps.tool.manage.views.user_can_migrate_version',
                lambda x,y: True)
            r.replace(
                'stars.apps.tool.manage.views.form_helpers.basic_save_form',
                lambda w,x,y,z: (None, True))
            r.replace(
                'stars.apps.tool.manage.views.perform_migration.delay',
                lambda x,y,z: None)
            _ = views.migrate_version(self.request)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('migration is in progress' in
                        info_message_divs[0].text)

    def test_purchase_subscription_discount_code_applied_message(self):
        """Does purchase_subscription show a msg when a discount code is used?
        """
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            r.replace('stars.apps.tool.manage.views.PaymentForm',
                      MockPaymentForm)
            r.replace(
                'stars.apps.tool.manage.views.get_payment_dict',
                lambda x,y: dict())
            r.replace(
                'stars.apps.tool.manage.views.process_payment',
                lambda x,y,invoice_num: dict())
            response = views.purchase_subscription(self.request)
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('Discount Code Applied' in
                        info_message_divs[0].text)

    def test_purchase_subscription_processing_error_error_message(self):
        """Does purchase_subscription show an error msg upon a processing error?
        """
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            r.replace('stars.apps.tool.manage.views.PaymentForm',
                      MockPaymentForm)
            r.replace(
                'stars.apps.tool.manage.views.get_payment_dict',
                lambda x,y: dict())
            r.replace(
                'stars.apps.tool.manage.views.process_payment',
                lambda x,y,invoice_num: { 'cleared': False,
                                          'msg': None })
            response = views.purchase_subscription(self.request)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('rocessing Error' in error_message_divs[0].text)

    def test_purchase_subscription_invalid_payform_error_message(self):
        """Does purchase_subscription show an error if payment form is invalid?
        """
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            response = views.purchase_subscription(self.request)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)

    def test_pay_subscription_discount_code_applied_message(self):
        """Does pay_subscription show a msg when a discount code is used?
        """
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            r.replace('stars.apps.tool.manage.views.PaymentForm',
                      MockPaymentForm)
            r.replace(
                'stars.apps.tool.manage.views.get_payment_dict',
                lambda x,y: dict())
            r.replace(
                'stars.apps.tool.manage.views.process_payment',
                lambda x,y,invoice_num: dict())
            response = views.pay_subscription(self.request,
                                              self.subscription.id)
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('Discount Code Applied' in
                        info_message_divs[0].text)

    def test_pay_subscription_processing_error_error_message(self):
        """Does pay_subscription show an error msg upon a processing error?
        """
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            r.replace('stars.apps.tool.manage.views.PaymentForm',
                      MockPaymentForm)
            r.replace(
                'stars.apps.tool.manage.views.get_payment_dict',
                lambda x,y: dict())
            r.replace(
                'stars.apps.tool.manage.views.process_payment',
                lambda x,y,invoice_num: { 'cleared': False,
                                          'msg': None })
            response = views.pay_subscription(self.request,
                                              self.subscription.id)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('rocessing Error' in error_message_divs[0].text)

    def test_pay_subscription_invalid_payform_error_message(self):
        """Does pay_subscription show an error when payment form is invalid?
        """
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            response = views.pay_subscription(self.request,
                                              self.subscription.id)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)


class MockAccountForm(object):

    def __init__(self, *args, **kwargs):
        self.cleaned_data = {'email': "doesn't matter",
                             'userlevel': "doesn't matter"}

    def is_valid(self):
        return True


class MockPaymentForm(object):

    def __init__(self, *args, **kwargs):
        self.cleaned_data = { 'discount_code': 'ILOVETOSAVEMONEY' }

    def is_valid(self):
        return True


class _InstitutionAdminToolMixinTest(TestCase):
    """
        Provides a base TestCase that checks if a view;

            1. is non GET-able by non-admin users;

            2. is GET-able by admin users, and;

            3. returns a loadable (by an admin) success_url.
    """

    view_class = None  # Must be set in subclass.

    def setUp(self):
        self.institution = InstitutionFactory()

        self.account = StarsAccountFactory(institution=self.institution)
        self.account_to_edit = StarsAccountFactory(institution=self.institution)

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
        return self.account.id

    def test_get_by_non_admin(self):
        self.account.user_level = ''
        self.account.save()
        response = self.view_class.as_view()(
            self.request,
            institution_slug=self.institution.slug,
            pk=self._get_pk())
        self.assertEqual(response.status_code, 403)

    def test_get_by_admin(self):
        self.account.user_level = 'admin'
        self.account.save()
        response = self.view_class.as_view()(
            self.request,
            institution_slug=self.institution.slug,
            pk=self._get_pk())
        self.assertEqual(response.status_code, 200)

    def test_get_success_url_is_loadable(self):
        """Is the url returned by get_success_url() loadable?"""
        self.account.user_level = 'admin'
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


class AccountDeleteViewTest(_InstitutionAdminToolMixinTest):

    view_class = views.AccountDeleteView

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
