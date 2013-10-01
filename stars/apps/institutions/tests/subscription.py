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
from stars.test_factories import (InstitutionFactory, SubscriptionFactory,
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

    def test__apply_early_renewal_discount(self):
        price = 10000
        self.assertLess(self.subscription._apply_early_renewal_discount(price),
                        price)

    #################################
    # _calculate_reason() tests:
    #################################

    def test__calculate_reason_member_initial(self):
        """Does _calculate_reason work for an initial member subscription?
        """
        self.subscription.institution = self.member
        self.assertEqual(self.subscription._calculate_reason(),
                         'member_reg')

    def test__calculate_reason_nonmember_initial(self):
        """Does _calculate_reason work for initial nonmember subscription?
        """
        self.subscription.institution = self.nonmember
        self.assertEqual(self.subscription._calculate_reason(),
                         'nonmember_reg')

    def test__calculate_reason_member_renewal(self):
        """Does _calculate_reason work for a member renewal?
        """
        self.subscription.institution = self.member
        self.subscription.save()
        new_subscription = SubscriptionFactory(institution=self.member)
        self.assertEqual(new_subscription._calculate_reason(),
                         'member_renew')

    def test__calculate_reason_nonmember_renewal(self):
        """Does _calculate_reason work for a nonmember renewal?
        """
        self.subscription.institution = self.nonmember
        self.subscription.save()
        new_subscription = SubscriptionFactory(institution=self.nonmember)
        self.assertEqual(new_subscription._calculate_reason(),
                         'nonmember_renew')

    ################################
    # calculate_start_date() tests:
    ################################

    def test__calculate_start_date_lapsed_subscription(self):
        """Does _calculate_start_date work when subscription is lapsed?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Subscription.'
                      '_get_latest_subscription_end',
                      lambda x: date.today() - timedelta(days=200))
            start_date = self.subscription._calculate_start_date()
        self.assertEqual(start_date, date.today())

    def test__calculate_start_date_current_subscription(self):
        """Does _calculate_start_date work when subscription is current?
        """
        DAYS_UNTIL_SUB_EXPIRES = 200
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.institutions.models.Subscription.'
                '_get_latest_subscription_end',
                lambda x: (
                    date.today() + timedelta(days=DAYS_UNTIL_SUB_EXPIRES)))
            start_date = self.subscription._calculate_start_date()
        self.assertEqual(
            start_date,
            date.today() + timedelta(days=DAYS_UNTIL_SUB_EXPIRES + 1))

    def test__calculate_start_date_subscription_ends_today(self):
        """Does _calculate_start_date work when subscription ends today?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Subscription.'
                      '_get_latest_subscription_end',
                      lambda x: date.today())
            start_date = self.subscription._calculate_start_date()
        self.assertEqual(start_date, date.today() + timedelta(1))

    ####################################
    # qualifies_for_early_renewal_discount() tests:
    ####################################

    def test_qualifies_for_early_renewal_discount_no_previous_subscription(
            self):
        """Does qualifies_for_early_renewal_discount work if there's no
        prev subscription?
        """
        self.assertFalse(
            self.subscription.qualifies_for_early_renewal_discount())

    def test_qualifies_for_early_renewal_discount_current_subscription(self):
        """Does qualifies_for_early_renewal_discount work when a
        subscription is current?
        """
        current_start_date = date.today() - timedelta(days=5)
        current_end_date = date.today() + timedelta(days=5)
        SubscriptionFactory(institution=self.subscription.institution,
                            start_date=current_start_date,
                            end_date=current_end_date)
        self.assertTrue(
            self.subscription.qualifies_for_early_renewal_discount())

    def test_qualifies_for_early_renewal_discount_recently_lapsed_subscription(
            self):
        """Does qualifies_for_early_renewal_discount work when subs is
        recently lapsed?
        """
        lapsed_start_date = date.today() - timedelta(days=100)
        lapsed_end_date = date.today() - timedelta(days=5)
        SubscriptionFactory(institution=self.subscription.institution,
                            start_date=lapsed_start_date,
                            end_date=lapsed_end_date)
        self.assertTrue(
            self.subscription.qualifies_for_early_renewal_discount())

    def test_qualifies_for_early_renewal_discount_long_time_lapsed_subscription(
            self):
        """Does qualifies_for_early_renewal_discount work when a subs lapsed
        long time ago?
        """
        lapsed_start_date = date.today() - timedelta(days=1000)
        lapsed_end_date = date.today() - timedelta(days=900)
        SubscriptionFactory(institution=self.subscription.institution,
                            start_date=lapsed_start_date,
                            end_date=lapsed_end_date)
        self.assertFalse(
            self.subscription.qualifies_for_early_renewal_discount())

    #############################
    # _apply_promo_code() tests:
    #############################

    def test__apply_promo_code_amount(self):
        """Does _apply_promo_code work for a promo code with amount specified?
        """
        promo_amount = 43
        promo = ValueDiscountFactory(
            amount=promo_amount,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1))
        initial_price = 5432
        self.assertEqual(
            self.subscription._apply_promo_code(initial_price,
                                                promo.code),
            initial_price - promo_amount)

    def test__apply_promo_code_percentage(self):
        """Does _apply_promo_code work for percentage off promo code?
        """
        promo_percentage = 25
        promo = ValueDiscountFactory(
            amount=0,
            percentage=promo_percentage,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1))
        self.assertEqual(
            self.subscription._apply_promo_code(price=1000,
                                                promo_code=promo.code),
            750)

    def test__apply_promo_code_expired_promo_code(self):
        """Does _apply_promo_code work for an expired promo code?
        """
        promo_amount = 50
        promo = ValueDiscountFactory(
            amount=promo_amount,
            start_date=date.today() - timedelta(days=20),
            end_date=date.today() - timedelta(days=10))
        initial_price = 1000
        with self.assertRaises(ExpiredDiscountCodeError):
            self.subscription._apply_promo_code(initial_price,
                                                promo.code)

    def test__apply_promo_code_invalid_promo_code(self):
        """Does _apply_promo_code work for an invalid promo code?
        (Where 'invalid' means nonexistant.)
        """
        initial_price = 10
        with self.assertRaises(InvalidDiscountCodeError):
            self.subscription._apply_promo_code(initial_price,
                                                'BO-O-O-GUS CODE'),

    def test__apply_promo_code_no_promo_code(self):
        """Does _apply_promo_code work when no promo code is supplied?
        """
        initial_price = 10
        self.assertEqual(self.subscription._apply_promo_code(initial_price),
                         initial_price)

    def test__apply_promo_code_100_percent(self):
        """Does _apply_promo_code work when the promo is 100% off?
        """
        initial_price = 1400.99
        promo = ValueDiscountFactory(
            amount=0,
            percentage=100)
        self.assertEqual(self.subscription._apply_promo_code(initial_price,
                                                             promo.code),
                         0.0)

    ###########################
    # calculate_price() tests:
    ###########################

    def _test_calculate_price(self, is_member, use_promo,
                              gets_discount):
        """Tests calculate_price.

        is_member, use_promo, and gets_discount are booleans that map
        to the three qualities that influence a subscription's price.

        There are eight possible combinations:

            member, promo, discount
            member, no promo, discount
            member, promo, no discount
            member, no promo, no discount
            nonmember, promo, discount
            nonmember, no promo, discount
            nonmember, promo, no discount
            nonmember, no promo, no discount

        Individual tests below exercise these combinations.
        """
        self.subscription.institution = (self.member if is_member
                                         else self.nonmember)
        self.subscription.save()

        if use_promo:
            promo_code = 'WHO SAID THAT?'
            promo_amount = 50
            promo_discount = ValueDiscount(
                code=promo_code,
                amount=promo_amount,
                start_date=date.today() - timedelta(days=1),
                end_date=date.today() + timedelta(days=1))
            promo_discount.save()
        else:
            promo_code = None

        self.subscription.qualifies_for_early_renewal_discount = (
            lambda *args: gets_discount)

        prices = self.subscription.calculate_prices(promo_code=promo_code)

        price_check = (Subscription.MEMBER_BASE_PRICE if is_member else
                       Subscription.NONMEMBER_BASE_PRICE)

        if gets_discount:
            price_check = self.subscription._apply_early_renewal_discount(
                price_check)

        if promo_code:
            price_check -= promo_amount

        self.assertEqual(prices['total'], price_check)

    def test_calculate_price_member_promo_discount(self):
        """Does calculate_price work for member with promo and discount?
        """
        self._test_calculate_price(
            is_member=True, use_promo=True, gets_discount=True)

    def test_calculate_price_nonmember_promo_discount(self):
        """Does calculate_price work for nonmember with promo and discount?
        """
        self._test_calculate_price(
            is_member=False, use_promo=True, gets_discount=True)

    def test_calculate_price_member_no_promo_discount(self):
        """Does calculate_price work for member with no promo and discount?
        """
        self._test_calculate_price(
            is_member=True, use_promo=False, gets_discount=True)

    def test_calculate_price_nonmember_no_promo_discount(self):
        """Does calculate_price work for nonmember with no promo and discount?
        """
        self._test_calculate_price(
            is_member=False, use_promo=False, gets_discount=True)

    def test_calculate_price_member_no_promo_no_discount(self):
        """Does calculate_price work for member with no promo and no discount?
        """
        self._test_calculate_price(
            is_member=True, use_promo=False, gets_discount=False)

    def test_calculate_price_nonmember_no_promo_no_discount(self):
        """Does calculate_price work for nonmember with no promo & no discount?
        """
        self._test_calculate_price(
            is_member=False, use_promo=False, gets_discount=False)

    def test_calculate_price_member_promo_no_discount(self):
        """Does calculate_price work for member with promo and no discount?
        """
        self._test_calculate_price(
            is_member=True, use_promo=True, gets_discount=False)

    def test_calculate_price_nonmember_promo_no_discount(self):
        """Does calculate_price work for nonmember with promo and no discount?
        """
        self._test_calculate_price(
            is_member=False, use_promo=True, gets_discount=False)

    ######################
    # tests for create():
    ######################

    def test_create_subscription_not_saved(self):
        """Does create() return an unsaved Subscription?"""
        subscription = Subscription.create(institution=InstitutionFactory())
        self.assertEqual(subscription.id, None)

    def test_create_with_promo_code(self):
        """Does create() work when a promo code is supplied?"""
        promo = ValueDiscountFactory(
            start_date=date.today(),
            end_date=date.today() + timedelta(days=100),
            amount=10)
        subscription = None
        subscription = Subscription.create(
            institution=InstitutionFactory(),
            promo_code=promo.code)
        self.assertIsNotNone(subscription)

    def test_create_without_promo_code(self):
        """Does create() work when a promo code is not supplied?"""
        subscription = None
        subscription = Subscription.create(
            institution=InstitutionFactory())
        self.assertIsNotNone(subscription)

    ###################################################
    # tests for get_date_range_for_new_subscription():
    ###################################################

    def test_get_date_range_for_new_subscription_current_sub(self):
        """get_date_range_for_new_subscription ok when inst has current subrx?
        """
        institution = InstitutionFactory()
        current_subscription = SubscriptionFactory(
            institution=institution,
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=5))
        (new_start_date,
         new_end_date) = Subscription.get_date_range_for_new_subscription(
            institution=institution)
        self.assertTrue(
            (new_start_date == current_subscription.end_date +
                               timedelta(days=1)) and
            (new_end_date == new_start_date +
                             timedelta(SUBSCRIPTION_DURATION)))

    def test_get_date_range_for_new_subscription_lapsed_sub(self):
        """get_date_range_for_new_subscription ok when inst has lapsed subrx?
        """
        institution = InstitutionFactory()
        _ = SubscriptionFactory(
            institution=institution,
            start_date=date.today() - timedelta(days=500),
            end_date=date.today() - timedelta(days=100))
        (new_start_date,
         new_end_date) = Subscription.get_date_range_for_new_subscription(
            institution=institution)
        self.assertTrue(
            (new_start_date == date.today()) and
            (new_end_date == new_start_date + timedelta(SUBSCRIPTION_DURATION)))

    def test_get_date_range_for_new_subscription_initial_sub(self):
        """get_date_range_for_new_subscription ok for inst's initial subrx?
        """
        institution = InstitutionFactory()
        (new_start_date,
         new_end_date) = Subscription.get_date_range_for_new_subscription(
            institution=institution)
        self.assertTrue(
            (new_start_date == date.today()) and
            (new_end_date == new_start_date + timedelta(SUBSCRIPTION_DURATION)))

    def test_get_date_range_for_new_subscription_current_sub_ends_today(self):
        """get_date_range_for_new_subscription ok if current subrx ends today?
        """
        institution = InstitutionFactory()
        _ = SubscriptionFactory(
            institution=institution,
            start_date=date.today() - timedelta(days=500),
            end_date=date.today())
        (new_start_date,
         new_end_date) = Subscription.get_date_range_for_new_subscription(
            institution=institution)
        self.assertTrue(
            (new_start_date == date.today() + timedelta(days=1)) and
            (new_end_date == new_start_date + timedelta(SUBSCRIPTION_DURATION)))

    ###################
    # tests for pay():
    ###################

    def test_pay_creates_payment_with_good_credit_card_info(self):
        """Does pay create a payment when it gets good credit card info?"""
        subscription = SubscriptionFactory(amount_due=500)
        subscription.pay(user=UserFactory(),
                         amount=subscription.amount_due,
                         card_num=GOOD_CREDIT_CARD,
                         exp_date='102020')
        self.assertEqual(subscription.subscriptionpayment_set.count(), 1)

    def test_pay_creates_payment_for_correct_amount(self):
        """Does pay create a payment for the correct amount?"""
        SUBSCRIPTION_PRICE = 350
        subscription = SubscriptionFactory(amount_due=SUBSCRIPTION_PRICE)
        subscription_payment = subscription.pay(
            user=UserFactory(),
            amount=subscription.amount_due,
            card_num=GOOD_CREDIT_CARD,
            exp_date='102020')
        self.assertEqual(subscription_payment.amount,
                         SUBSCRIPTION_PRICE)

    def test_pay_does_not_create_payment_with_bad_credit_card_info(self):
        """Does pay not create a payment when it gets bad credit card info?"""
        subscription = SubscriptionFactory(amount_due=500)
        try:
            subscription.pay(user=UserFactory(),
                             amount=subscription.amount_due,
                             card_num=BAD_CREDIT_CARD,
                             exp_date='102020')
        except CreditCardProcessingError:
            self.assertEqual(subscription.subscriptionpayment_set.count(), 0)
        else:
            self.fail('credit card transaction should have failed')

    def test_pay_updates_amount_due(self):
        """Does a payment decrease the amount due?"""
        unpaid_amount = 100
        subscription = SubscriptionFactory(amount_due=500.75)
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.payments.credit_card.'
                      'CreditCardPaymentProcessor',
                      MockCreditCardPaymentProcessor)
            subscription.pay(user=UserFactory(),
                             amount=subscription.amount_due - unpaid_amount,
                             card_num=GOOD_CREDIT_CARD,
                             exp_date='102020')
        self.assertEqual(subscription.amount_due, unpaid_amount)

    def test_pay_full_amount_due_updates_paid_in_full(self):
        """Does a full payment turn paid_in_full on?"""
        subscription = SubscriptionFactory(amount_due=500.99)
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.payments.credit_card.'
                      'CreditCardPaymentProcessor',
                      MockCreditCardPaymentProcessor)
            subscription.pay(user=UserFactory(),
                             amount=subscription.amount_due,
                             card_num=GOOD_CREDIT_CARD,
                             exp_date='102020')
        self.assertTrue(subscription.paid_in_full)

    def test_pay_partial_amount_due_does_not_update_paid_in_full(self):
        """Does a full payment turn paid_in_full on?"""
        subscription = SubscriptionFactory(amount_due=500.99)
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.payments.credit_card.'
                      'CreditCardPaymentProcessor',
                      MockCreditCardPaymentProcessor)
            subscription.pay(user=UserFactory(),
                             amount=subscription.amount_due - .10,
                             card_num=GOOD_CREDIT_CARD,
                             exp_date='102020')
        self.assertFalse(subscription.paid_in_full)

    ########################
    # tests for purchase():
    ########################

    def test_purchase_pay_now_creates_payment(self):
        """Does purchase create a payment when user wants to pay now?
        """
        subscription = Subscription.purchase(
            institution=self.subscription.institution,
            pay_when=Subscription.PAY_NOW,
            user=UserFactory(),
            card_num=GOOD_CREDIT_CARD,
            exp_date='102020')
        self.assertEqual(subscription.subscriptionpayment_set.count(), 1)

    def test_purchase_pay_now_creates_payment_for_correct_amount(self):
        """Does purchase create a payment for the correct amount?

        Depends on Subscription.get_prices_for_new_subscription().
        """
        prices = Subscription.get_prices_for_new_subscription(
            institution=self.subscription.institution)
        Subscription.purchase(institution=self.subscription.institution,
                              pay_when=Subscription.PAY_NOW,
                              user=UserFactory(),
                              card_num=GOOD_CREDIT_CARD,
                              exp_date='102020')
        self.assertEqual(SubscriptionPayment.objects.reverse()[0].amount,
                         prices['total'])

    def test_purchase_pay_later_creates_no_payment(self):
        """Does purchase *not* create a payment if user wants to pay later?
        """
        initial_payment_count = SubscriptionPayment.objects.count()
        Subscription.purchase(institution=self.subscription.institution,
                              pay_when=Subscription.PAY_LATER,
                              user=UserFactory())
        self.assertEqual(initial_payment_count,
                         SubscriptionPayment.objects.count())

    def test_purchase_institution_updated(self):
        """Does purchase update the subscription's institution?
        """
        institution = InstitutionFactory()
        subscription = Subscription.purchase(institution=institution,
                                             pay_when=Subscription.PAY_LATER,
                                             user=UserFactory())
        self.assertEqual(institution.current_subscription, subscription)
        self.assertTrue(institution.is_participant)

    def test_purchase_sends_email(self):
        """Does purchase send any post-purchase email?
        """
        initial_outgoing_mails = len(mail.outbox)
        Subscription.purchase(institution=self.subscription.institution,
                              pay_when=Subscription.PAY_LATER,
                              user=UserFactory())
        self.assertLess(initial_outgoing_mails, len(mail.outbox))

    def test_purchase_does_not_send_email_if_credit_card_is_declined(self):
        """Does purchase send no email if credit card is declined?

           Depends on Subscription.create().
        """
        initial_outgoing_mails = len(mail.outbox)
        try:
            Subscription.purchase(institution=self.subscription.institution,
                                  pay_when=Subscription.PAY_NOW,
                                  user=UserFactory(),
                                  card_num=BAD_CREDIT_CARD,
                                  exp_date='102020')
        except SubscriptionPurchaseError:
            self.assertEqual(initial_outgoing_mails, len(mail.outbox))
        else:
            self.fail('credit card transaction should have failed')

    def test_purchase_pay_later_sends_one_email(self):
        """Does purchase send one email when user pays later?
        """
        initial_outgoing_mails = len(mail.outbox)
        Subscription.purchase(institution=self.subscription.institution,
                              pay_when=Subscription.PAY_LATER,
                              user=UserFactory())
        self.assertEqual(initial_outgoing_mails + 1, len(mail.outbox))

    def test_purchase_pay_now_renewal_sends_an_email(self):
        """Does purchase send an email when a user pays now for a renewal?
        """
        initial_outgoing_mails = len(mail.outbox)
        Subscription.purchase(institution=self.subscription.institution,
                              pay_when=Subscription.PAY_NOW,
                              user=UserFactory(),
                              card_num=GOOD_CREDIT_CARD,
                              exp_date='102020')
        self.assertEqual(initial_outgoing_mails + 1, len(mail.outbox))

    def test_purchase_pay_now_first_subrx_sends_one_email(self):
        """Does purchase send one email when user pays now for first subrx?

           Depends on Subscription.create().
        """
        initial_outgoing_mails = len(mail.outbox)
        institution = InstitutionFactory()
        Subscription.purchase(institution=institution,
                              pay_when=Subscription.PAY_NOW,
                              user=UserFactory(),
                              card_num=GOOD_CREDIT_CARD,
                              exp_date='102020')
        self.assertEqual(initial_outgoing_mails + 1, len(mail.outbox))

    def test_purchase_mails_user_if_not_contact_email(self):
        """Does user get email if he's not institution.contact_email?
        """
        contact_email = 'jim@jonestown.gy'
        user_email = 'teddy@kozinski.nom'
        institution = InstitutionFactory(contact_email=contact_email)
        user = UserFactory(email=user_email)
        Subscription.purchase(institution=institution,
                              pay_when=Subscription.PAY_LATER,
                              user=user)
        message = mail.outbox.pop()
        self.assertEqual(message.to, [contact_email, user_email])

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

    @_test_email_templates_ok
    def test_purchase_pay_now_registration_email_templates_ok(self):
        """Are the email templates used when paying now for registration ok?

           Where "ok" means they get the context they're expecting.
        """
        institution = InstitutionFactory()
        Subscription.purchase(institution=institution,
                              pay_when=Subscription.PAY_NOW,
                              user=UserFactory(),
                              card_num=GOOD_CREDIT_CARD,
                              exp_date='102020')

    @_test_email_templates_ok
    def test_purchase_pay_later_registration_email_templates_ok(self):
        """Are the email templates used when paying later for registration ok?

           Where "ok" means they get the context they're expecting.
        """
        Subscription.purchase(institution=self.subscription.institution,
                              pay_when=Subscription.PAY_LATER,
                              user=UserFactory())

    @_test_email_templates_ok
    def test_purchase_pay_now_renewal_email_templates_ok(self):
        """Are the email templates used when paying later for registration ok?

           Where "ok" means they get the context they're expecting.
        """
        Subscription.purchase(institution=self.subscription.institution,
                              pay_when=Subscription.PAY_NOW,
                              user=UserFactory(),
                              card_num=GOOD_CREDIT_CARD,
                              exp_date='102020')

    @_test_email_templates_ok
    def test_purchase_pay_later_renewal_email_templates_ok(self):
        """Are the email templates used when paying later for registration ok?

           Where "ok" means they get the context they're expecting.
        """
        Subscription.purchase(institution=self.subscription.institution,
                              pay_when=Subscription.PAY_LATER,
                              user=UserFactory())
