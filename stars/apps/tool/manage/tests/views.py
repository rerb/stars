"""Tests for apps/tool/manage/views.py.
"""
import datetime
import time

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render
from django.test import TestCase
from django.test.client import RequestFactory
import factory
import testfixtures

from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import Institution, PendingAccount, \
     Subscription, SubscriptionPayment, StarsAccount
from stars.apps.registration.models import ValueDiscount
from stars.apps.submissions.models import ResponsibleParty, SubmissionSet
from stars.apps.tool.manage import views


class ViewsTest(TestCase):

    fixtures = ['responsible_party_test_data.json']

    def setUp(self):
        self.request = HttpRequest()
        self.request.user = User.objects.get(pk=1)
        self.request.institution = Institution.objects.get(pk=1)
        self.request.user.current_inst = self.request.institution
        self.request.user.has_perm = lambda x: True
        self.request.session = {}
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

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def test_delete_responsible_party_credit_count_error_message(self):
        """Does delete_responsible_party show an error if credit_count > 0?
        """
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.accounts.decorators._get_account_problem_response',
                lambda x: False)
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            _ = views.delete_responsible_party(self.request, 1)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('cannot be removed' in info_message_divs[0].text)

    def test_delete_responsible_party_success_message(self):
        """Does delete_responsible_party show a success message when all is ok?
        """
        submissionset = SubmissionSet.objects.get(pk=1)
        submissionset.is_visible = False
        submissionset.save()
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.accounts.decorators._get_account_problem_response',
                lambda x: False)
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            _ = views.delete_responsible_party(self.request, 1)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('uccessfully Removed' in info_message_divs[0].text)

    def test_add_account_nonexistent_user(self):
        """Does add_account show an error if a nonexistent user is specified?
        """
        self.request.method = 'POST'
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.accounts.decorators._get_account_problem_response',
                lambda x: False)
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            r.replace(
                'stars.apps.tool.manage.views.AccountForm', MockAccountForm)
            r.replace(
                'stars.apps.tool.manage.views.xml_rpc.get_user_by_email',
                lambda x : None)
            _ = views.add_account(self.request)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('no AASHE user with e-mail'
                        in info_message_divs[0].text)

    def test_delete_account_pending_account_message(self):
        """Does delete_account display a msg if the account is pending?
        """
        pending_account = PendingAccount()
        pending_account.id = -999
        pending_account.institution = self.request.institution
        pending_account.save()
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.accounts.decorators._get_account_problem_response',
                lambda x: False)
            r.replace(
                'stars.apps.tool.manage.views._get_current_institution',
                lambda x: self.request.institution)
            _ = views.delete_account(request=self.request, account_id=-999)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        success_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.SUCCESS]})
        self.assertEqual(len(success_message_divs), 1)
        self.assertTrue('ending account:' and 'successfully deleted' in
                        success_message_divs[0].text)

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


class InstitutionFactory(factory.Factory):
    FACTORY_FOR = Institution

    enabled = True
    slug = factory.Sequence(
        lambda i: 'test-inst-{0}-{1}'.format(i, time.time()))


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(
        lambda i: 'testuser-{0}.{1}'.format(i, time.time()))


class StarsAccountFactory(factory.Factory):
    FACTORY_FOR = StarsAccount

    institution = factory.SubFactory(InstitutionFactory)
    user = factory.SubFactory(UserFactory)


class SubscriptionFactory(factory.Factory):
    FACTORY_FOR = Subscription

    institution = factory.SubFactory(InstitutionFactory)
    start_date = '1970-01-01'
    end_date = datetime.date.today()
    amount_due = 1000.00


class SubscriptionPaymentFactory(factory.Factory):
    FACTORY_FOR = SubscriptionPayment

    subscription = factory.SubFactory(SubscriptionFactory)
    date = datetime.date.today()
    amount = 50.00
    user = factory.SubFactory(UserFactory)


class InstitutionPaymentsViewTest(TestCase):

    def setUp(self):
        self.institution = InstitutionFactory()

        self.account = StarsAccountFactory(institution=self.institution)

        subscription = SubscriptionFactory(institution=self.institution)
        for i in range(4):
            SubscriptionPaymentFactory(subscription=subscription)

        self.request = RequestFactory()
        self.request.user = self.account.user
        self.request.user.current_inst = self.account.institution
        self.request.method = 'GET'

    def test_request_by_non_admin(self):
        self.account.user_level = ''
        self.account.save()
        response = views.InstitutionPaymentsView.as_view()(
            self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(response.status_code, 403)

    def test_request_by_admin(self):
        self.account.user_level = 'admin'
        self.account.save()
        response = views.InstitutionPaymentsView.as_view()(
            self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(response.status_code, 200)


class ResponsiblePartyFactory(factory.Factory):
    FACTORY_FOR = ResponsibleParty

    institution = factory.SubFactory(InstitutionFactory)


class ResponsiblePartyListViewTest(TestCase):

    def setUp(self):
        self.institution = InstitutionFactory()

        self.account = StarsAccountFactory(institution=self.institution)

        for i in range(4):
            _ = ResponsiblePartyFactory(institution=self.institution)

        self.request = RequestFactory()
        self.request.user = self.account.user
        self.request.user.current_inst = self.account.institution
        self.request.method = 'GET'

    def test_request_by_non_admin(self):
        self.account.user_level = ''
        self.account.save()
        response = views.InstitutionPaymentsView.as_view()(
            self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(response.status_code, 403)

    def test_request_by_admin(self):
        self.account.user_level = 'admin'
        self.account.save()
        response = views.InstitutionPaymentsView.as_view()(
            self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(response.status_code, 200)


class ResponsiblePartyEditViewTest(TestCase):

    def setUp(self):
        self.institution = InstitutionFactory()

        self.account = StarsAccountFactory(institution=self.institution)

        self.responsible_parties = [
            ResponsiblePartyFactory(institution=self.institution) for i
            in range(4)]

        self.request = RequestFactory()
        self.request.user = self.account.user
        self.request.method = 'GET'

    def test_get_by_non_admin(self):
        self.account.user_level = ''
        self.account.save()
        response = views.ResponsiblePartyEditView.as_view()(
            self.request,
            institution_slug=self.institution.slug,
            pk=self.responsible_parties[0].id)
        self.assertEqual(response.status_code, 403)

    def test_get_by_admin(self):
        self.account.user_level = 'admin'
        self.account.save()
        response = views.ResponsiblePartyEditView.as_view()(
            self.request,
            institution_slug=self.institution.slug,
            pk=self.responsible_parties[0].id)
        self.assertEqual(response.status_code, 200)
