"""Tests for apps.registration.views.
"""
from unittest import TestCase

from django.http import HttpRequest
import testfixtures

from stars.apps.institutions.models import Institution
from stars.apps.registration import views


class ViewsTest(TestCase):

    def test_select_institution_logging(self):
        """Does select_institution log an error for an invalid form?
        """
        with testfixtures.LogCapture('stars') as log:
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
        self.assertTrue(log.records[0].module_path.startswith('stars'))
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
        self.assertTrue(log.records[0].module_path.startswith('stars'))
        self.assertTrue('Payment denied' in log.records[0].msg)

    def test__get_registration_price_logging(self):
        """Does _get_registration_price log a warning for an invalid coupon?
        """
        institution = Institution()
        with testfixtures.LogCapture('stars') as log:
            views._get_registration_price(institution=institution,
                                          discount_code='bo-o-o-o-gus coupon')

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'WARNING')
        self.assertTrue(log.records[0].module_path.startswith('stars'))
        self.assertTrue('Invalid Coupon Code' in log.records[0].msg)


class MockRequest(HttpRequest):

    def __init__(self):
        super(HttpRequest, self).__init__()
        self.method = 'POST'
        self.POST = None
        # path and META are here for logging formatters:
        self.path = '/mock/request/bogus/path'
        self.META = {}
        self.environ = {}


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
