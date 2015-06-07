"""Tests for apps/payments/simple_credit_card.py.
"""
from logging import getLogger, CRITICAL
import os

from django.test import TestCase

from stars.apps.payments import simple_credit_card
from stars.test_factories import SubscriptionFactory, UserFactory

# Don't bother me:
logger = getLogger('stars')
logger.setLevel(CRITICAL)

GOOD_CREDIT_CARD = '4007000000027'  # good test credit card number
BAD_CREDIT_CARD = '123412341234'


class MockPaymentForm(object):

    def __init__(self, cleaned_data=[]):
        self.cleaned_data = cleaned_data


class SimpleCreditCardPaymentProcessorTest(TestCase):

    def setUp(self):
        self.ccpp = simple_credit_card.CreditCardPaymentProcessor()
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
        payment = self.ccpp.process_subscription_payment(
            subscription=self.subscription,
            user=self.user,
            amount=19.95,
            card_num=GOOD_CREDIT_CARD,
            exp_date='022022',
            cvv='123')
        self.assertEqual(payment.amount, 19.95)

    def test_process_subscription_payment_handles_invalid_cc_number(self):
        """Does process_subscription_payment() handle invalid CC numbers ok?
        """
        self.valid_payment_form.cleaned_data['card_number'] = BAD_CREDIT_CARD
        self.assertRaises(simple_credit_card.CreditCardProcessingError,
                          self.ccpp.process_subscription_payment,
                          subscription=self.subscription,
                          user=self.user,
                          amount=19.95,
                          card_num=BAD_CREDIT_CARD,
                          exp_date='022022',
                          cvv='123')

    def test__process_payment(self):
        """Does _process_payment() work?"""
        result = self.ccpp._process_payment(card_num=GOOD_CREDIT_CARD,
                                            exp_date='022022',
                                            cvv='123',
                                            products=self.product_list)
        self.assertEquals(True, result['cleared'])
        self.assertGreater(result['conf'], '')
        self.assertGreater(result['trans_id'], '')

    def test__process_payment_handles_invalid_cc_number(self):
        """Does _process_payment() handle invalid CC numbers gracefully?
        """
        self.assertRaises(simple_credit_card.CreditCardProcessingError,
                          self.ccpp._process_payment,
                          card_num=BAD_CREDIT_CARD,
                          exp_date='022022',
                          cvv='123',
                          products=self.product_list,
                          login=self.login,
                          key=self.key)
