"""Tests for apps.institutions.models.Subscription.
"""
from datetime import date, timedelta
from functools import wraps
from logging import getLogger, CRITICAL
import re

from django.conf import settings
from django.core import mail
from django.test import TestCase
import testfixtures

from stars.apps.institutions.models import (Subscription,
                                            SubscriptionPayment,
                                            SubscriptionPurchaseError,
                                            SUBSCRIPTION_DURATION)
from stars.apps.payments.simple_credit_card import (CreditCardPaymentProcessor,
                                                    CreditCardProcessingError)
from stars.apps.registration.models import (ExpiredDiscountCodeError,
                                            InvalidDiscountCodeError,
                                            ValueDiscount)
from stars.test_factories.models import (InstitutionFactory, SubscriptionFactory,
                                         UserFactory, ValueDiscountFactory)

# Don't bother me:
logger = getLogger('stars')
logger.setLevel(CRITICAL)

GOOD_CREDIT_CARD = '4007000000027'  # good test credit card number
BAD_CREDIT_CARD = '123412341234'


class MockCreditCardPaymentProcessor(CreditCardPaymentProcessor):
    """For mocking the actual credit card payment processing."""

    def process_subscription_payment(self, *args, **kwargs):
        return (None, None)


class SubscriptionTest(TestCase):

    fixtures = ['email_templates.json']

    def setUp(self):
        self.subscription = SubscriptionFactory(
            institution=InstitutionFactory())
        self.member = InstitutionFactory(is_member=True)
        self.nonmember = InstitutionFactory(is_member=False)

    #################################
    # _calculate_reason() tests:
    #################################

    # _calculate_reason() removed from class Subscription

    ################################
    # calculate_start_date() tests:
    ################################

    # calculate_start_date() removed from class Subscription

    ####################################
    # qualifies_for_early_renewal_discount() tests:
    ####################################

    # qualifies_for_early_renewal_discount() removed from class Subscription

    #############################
    # _apply_promo_code() tests:
    #############################

    # _apply_promo_code() removed from class Subscription

    ###########################
    # calculate_price() tests:
    ###########################

    # calculate_price() removed from class Subscription

    ######################
    # tests for create():
    ######################

    # create() removed from class Subscription

    ###################################################
    # tests for get_date_range_for_new_subscription():
    ###################################################

    # get_date_range_for_new_subscription() removed from class Subscription

    ###################
    # tests for pay():
    ###################

    # pay() was removed from class Subscription

    ########################
    # tests for purchase():
    ########################

    # purchase() was removed from class Subscription

    ###################################################################
    # test that the email templates get the context they're expecting:
    ###################################################################

    def _invalid_template_strings(self, text, marker=None):
        marker = marker or settings.TEMPLATE_STRING_IF_INVALID
        invalid_strings = []
        for match in re.finditer(marker.replace('%s', '(.*)'),
                                 text):
            invalid_strings.append(match.groups()[0])
        return invalid_strings or None

    def _test_email_templates_ok(actual_test):
        @wraps(actual_test)
        def _test(self):
            settings.TEMPLATE_STRING_IF_INVALID = (
                'INVALID TEMPLATE STRING %s /INVALID TEMPLATE STRING')

            actual_test(self)

            for message in mail.outbox:
                invalid_strings = self._invalid_template_strings(message.body)
                self.assertIsNone(invalid_strings,
                                  msg=("invalid template string(s): " +
                                       str(invalid_strings)))
        return _test
