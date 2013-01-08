"""Tests for apps.registration.views.
"""
from unittest import TestCase

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest
import testfixtures

from stars.apps.institutions.models import Institution
from stars.apps.registration import views


class ViewsTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.user = User(username='sophisticate')
        self.user.save()
        self.request.user = self.user
        self.request.session = {}

        self.institution = Institution.objects.create()
        self.institution.save()

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def tearDown(self):
        self.user.delete()
        self.institution.delete()

    def test_reg_select_institution_logging(self):
        """Does reg_select_institution log an error for an invalid form?
        """
        with testfixtures.LogCapture('stars.request') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.registration.views._confirm_login',
                          lambda x: False)
                r.replace(
                    'stars.apps.registration.views.RegistrationSchoolChoiceForm',
                          MockRegistrationSchoolChoiceForm)
                r.replace('stars.apps.registration.views.respond',
                          lambda x,y,z: None)
                views.reg_select_institution(MockRequest())

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue('form didn\'t validate' in log.records[0].msg)

    def test_process_payment_logging(self):
        """Does process_payment log a warning if a payment is not approved?
        """
        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.registration.views.CcProcessor',
                          MockCcProcessor)
                views.process_payment(
                    payment_dict={'cc_number': None,
                                  'exp_date': None,
                                  'billing_address': None,
                                  'billing_city': None,
                                  'billing_state': None,
                                  'billing_zipcode': None,
                                  'billing_firstname': 'Tom',
                                  'billing_lastname': 'Joad',
                                  'cv_number': None,
                                  'country': None},
                    product_list=[])

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'WARNING')
        self.assertTrue('Payment denied' in log.records[0].msg)

    def test_get_registration_price_logging(self):
        """Does get_registration_price log a warning for an invalid coupon?
        """
        institution = Institution()
        with testfixtures.LogCapture('stars') as log:
            views.get_registration_price(institution=institution,
                                         discount_code='bo-o-o-o-gus coupon')

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'WARNING')
        self.assertTrue('Invalid Coupon Code' in log.records[0].msg)

    def test_select_participation_level_invalid_form_error_message(self):
        """Does select_participation_level display an error message
        when the input form is invalid?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.registration.views._get_selected_institution',
                      lambda x: (None, None))
            response = views.select_participation_level(self.request)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)

    def test_contact_info_step_invalid_form_error_message(self):
        """Does contact_info_step display an error message when the input
        form is invalid?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.registration.views._get_selected_institution',
                      lambda x: (None, None))
            response = views.contact_info_step(
                request=self.request,
                FormClass=MockFormClass,
                success_url="http://bogus",
                template_name="registration/select_participation_level.html")
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)

    def test_participant_contact_info_invalid_form_error_message(self):
        """Does test_participant_contact_info display an error message when
        the input form is invalid?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.registration.views._get_selected_institution',
                      lambda x: (None, None))
            response = views.particpant_contact_info(self.request)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)

    def test_respondent_contact_info_invalid_form_error_message(self):
        """Does respondent_contact_info display an error message when
        the input form is invalid?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.registration.views._get_selected_institution',
                      lambda x: (None, None))
            response = views.respondent_contact_info(self.request)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)

    def test_reg_payment_invalid_form_error_message(self):
        """Does reg_payment display an error message when input form is invalid?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.registration.views._get_selected_institution',
                      lambda x: (Institution.objects.create(), None))
            r.replace('stars.apps.registration.views.get_registration_price',
                      lambda *args: None)
            response = views.reg_payment(self.request)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)

    def test_reg_payment_processing_error_message(self):
        """Does reg_payment display an error message when there's a processing
        error?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.registration.views._get_selected_institution',
                      lambda x: (Institution.objects.create(), None))
            r.replace('stars.apps.registration.views.get_registration_price',
                      lambda *args: None)
            r.replace('stars.apps.registration.views.PaymentForm',
                      MockPaymentForm),
            r.replace('stars.apps.registration.views.PayLaterForm',
                      MockPayLaterForm),
            r.replace('stars.apps.registration.views.get_payment_dict',
                      lambda x,y: {})
            r.replace('stars.apps.registration.views.process_payment',
                      lambda x,y,invoice_num: {
                          'cleared': False,
                          'msg': None,
                          'trans_id': None })
            response = views.reg_payment(self.request)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('Processing Error' in error_message_divs[0].text)

    def test_reg_payment_discount_applied_message(self):
        """Does reg_payment display a message when a discount is applied?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.registration.views._get_selected_institution',
                      lambda x: (self.institution, None))
            r.replace('stars.apps.registration.views.get_registration_price',
                      lambda *args, **kwargs: None)
            r.replace('stars.apps.registration.views.PaymentForm',
                      MockPaymentDiscountedForm)
            r.replace('stars.apps.registration.views.PayLaterForm',
                      MockPayLaterForm),
            r.replace('stars.apps.registration.views.get_payment_dict',
                      lambda x,y: {})
            r.replace('stars.apps.registration.views.process_payment',
                      lambda x,y,invoice_num: {})
            response = views.reg_payment(self.request)
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('iscount' and 'pplied' in info_message_divs[0].text)

    def test_reg_account_no_institution_selected_error_message(self):
        """Does reg_account display an error msg if no institution is selected?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.registration.views._confirm_login',
                      lambda x: None)
            self.request.user.account = None
            response = views.reg_account(self.request)
        response = self.message_middleware.process_response(self.request,
                                                            response)
        self.assertTrue('messages' in response.cookies.keys())
        self.assertTrue('No Registered Institution Selected'
                        in response.cookies['messages'].js_output())

    def test__get_selected_institution_no_institution_selected_error_message(
            self):
        """Does _get_selected_institution show error msg if no inst is selected?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.registration.views._confirm_login',
                      lambda x: None)
            _, response = views._get_selected_institution(self.request)
        response = self.message_middleware.process_response(self.request,
                                                            response)
        self.assertTrue('messages' in response.cookies.keys())
        self.assertTrue('No Institution Selected'
                        in response.cookies['messages'].js_output())

class RegistrationSurveyViewTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.user = User(username='sophisticate')
        self.user.save()
        self.request.user = self.user
        self.request.session = {}

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def tearDown(self):
        self.user.delete()

    def test_render_no_institution_selected_error_message(self):
        """Does render display an error message if no institution is selected?
        """
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.registration.views.RegistrationSurveyView.'
                'get_institution', lambda x,y: None)
            registration_survey_view = views.RegistrationSurveyView(
                None, None, None)
            response = registration_survey_view.render(self.request)
        response = self.message_middleware.process_response(self.request,
                                                            response)
        self.assertTrue('messages' in response.cookies.keys())
        self.assertTrue('No Registered Institution Selected'
                        in response.cookies['messages'].js_output())


class MockPayLaterForm(object):

    def __init__(self, *args, **kwargs):
        self.cleaned_data = { 'confirm': False }

    def is_valid(self):
        return True


class MockPaymentForm(object):

    def __init__(self, *args, **kwargs):
        self.cleaned_data = { 'discount_code': None }

    def is_valid(self):
        return True


class MockPaymentDiscountedForm(object):

    def __init__(self, *args, **kwargs):
        self.cleaned_data = { 'discount_code': 'SUMMEROLOVE' }

    def is_valid(self):
        return True


class MockRequest(HttpRequest):

    def __init__(self):
        super(HttpRequest, self).__init__()
        self.method = 'POST'
        self.POST = None
        # path and META are here for logging formatters:
        self.path = '/mock/request/bogus/path'
        self.META = {'SERVER_NAME': 'joe',
                     'SERVER_PORT': 10}
        self.environ = {}
        self.user = User(username='jimmy_smits')
        self.host = 'hamlin'

    def get(self, *args, **kwargs):
        return ''


class MockRegistrationSchoolChoiceForm(object):

    def __init__(self, *args):
        self.errors = None
        self.fields = {'aashe_id': MockWidget()}

    def is_valid(self):
        return False


class MockWidget(object):

    def __init__(self):
        self.widget = None


class MockCcProcessor(object):

    def __init__(self, *args, **kwargs):
        pass

    def authorize(self, *args, **kwargs):
        return MockResult()


class MockResult(object):

    def __init__(self):
        self.response = 'REJECTED!!! SHAME!!! BAD CONSUMER!!! NO VOTE FOR YOU!!!'
        self.response_reason = 'NO CREDIT FOR MALCONTENTS!'

class MockFormClass(object):

    def __init__(self, request=None, instance=None):
        pass

    def is_valid(self):
        return False
