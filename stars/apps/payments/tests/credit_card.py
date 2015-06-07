"""Tests for apps/payments/credit_card.py.
"""
from logging import getLogger, CRITICAL
import os

from django.test import TestCase

from stars.apps.payments import credit_card
from stars.test_factories import SubscriptionFactory, UserFactory

# Don't bother me:
logger = getLogger('stars')
logger.setLevel(CRITICAL)

GOOD_CREDIT_CARD = '4007000000027'  # good test credit card number
BAD_CREDIT_CARD = '123412341234'


class MockPaymentForm(object):

    def __init__(self, cleaned_data=[]):
        self.cleaned_data = cleaned_data


class CreditCardPaymentProcessorTest(TestCase):

    def setUp(self):
        self.ccpp = credit_card.CreditCardPaymentProcessor()
        self.valid_payment_context = {
            'cc_number': GOOD_CREDIT_CARD,
            'exp_date': '122020',
            'cv_number': '123'
        }
        self.valid_payment_form = MockPaymentForm(
            {
                'card_number': GOOD_CREDIT_CARD,
                'exp_month': '12',
                'exp_year': '2020',
                'cv_code': '123'
            }
        )
        self.product_list = [{'name': 'test product',
                              'price': 19.95,
                              'quantity': 1}]
        self.login = os.environ.get('AUTHORIZENET_LOGIN', None)
        self.key = os.environ.get('AUTHORIZENET_KEY', None)
        self.user = UserFactory()
        self.subscription = SubscriptionFactory()

    def test_process_subscription_payment(self):
        """Does process_subscription_payment() work?"""
        payment, _ = self.ccpp.process_subscription_payment(
            subscription=self.subscription,
            amount=19.95,
            user=self.user,
            form=self.valid_payment_form)
        self.assertEqual(payment.amount, 19.95)

    def test_process_subscription_payment_handles_invalid_cc_number(self):
        """Does process_subscription_payment() handle invalid CC numbers ok?
        """
        self.valid_payment_form.cleaned_data['card_number'] = BAD_CREDIT_CARD
        self.assertRaises(credit_card.CreditCardProcessingError,
                          self.ccpp.process_subscription_payment,
                          subscription=self.subscription,
                          amount=99.95,
                          user=self.user,
                          form=self.valid_payment_form)

    def test_process_payment_form(self):
        """Does process_payment_form() work?"""
        result = self.ccpp.process_payment_form(
            amount=99.95,
            user=self.user,
            form=self.valid_payment_form,
            product_name='STARS Test Purchase')
        self.assertEquals(True, result['cleared'])
        self.assertGreater(result['conf'], '')
        self.assertGreater(result['trans_id'], '')

    def test_process_payment_form_handles_invalid_cc_number(self):
        """Does process_payment_form() handle invalid CC numbers gracefully?
        """
        self.valid_payment_form.cleaned_data['card_number'] = BAD_CREDIT_CARD
        self.assertRaises(credit_card.CreditCardProcessingError,
                          self.ccpp.process_payment_form,
                          amount=99.95,
                          user=self.user,
                          form=self.valid_payment_form,
                          product_name='STARS Test Purchase')

    def test__get_payment_context(self):
        """Does _get_payment_context() work?"""
        # Is this test even worth running?  Or does it just add fragility?
        payment_context = self.ccpp._get_payment_context(
            self.valid_payment_form)
        self.assertTrue('cc_number' in payment_context)
        self.assertTrue('exp_date' in payment_context)
        self.assertTrue('cv_number' in payment_context)

    def test__process_payment(self):
        """Does _process_payment() work?"""
        result = self.ccpp._process_payment(self.valid_payment_context,
                                            self.product_list,
                                            self.login,
                                            self.key)
        self.assertEquals(True, result['cleared'])
        self.assertGreater(result['conf'], '')
        self.assertGreater(result['trans_id'], '')

    def test__process_payment_handles_invalid_cc_number(self):
        """Does _process_payment() handle invalid CC numbers gracefully?
        """
        self.valid_payment_context['cc_number'] = BAD_CREDIT_CARD
        self.assertRaises(credit_card.CreditCardProcessingError,
                          self.ccpp._process_payment,
                          self.valid_payment_context,
                          self.product_list,
                          self.login,
                          self.key)

    # def test__process_payment_handles_payment_denied(self):
    #     """Does _process_payment() handle payment denied gracefully?
    #     """
    #     # How to force a payment denied response?
    #     # What's the thing to do?  Mock client.card(cc).capture()
    #     # so it returns exactly what we're testing for?
    #     result = self.ccpp._process_payment(self.valid_payment_context,
    #                                         self.product_list,
    #                                         self.login,
    #                                         self.key)
    #     self.assertEquals(False, result['cleared'])
    #     self.assertGreater(result['reason_code'], '')
    #     self.assertGreater(result['msg'], '')
