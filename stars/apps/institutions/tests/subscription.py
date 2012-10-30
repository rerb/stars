"""Tests for apps.institutions.models.Subscription.
"""
from datetime import date, timedelta
from unittest import TestCase

import testfixtures

from stars.apps.institutions.models import Subscription
from stars.apps.registration.models import ValueDiscount
from stars.test_factories import InstitutionFactory, SubscriptionFactory


class SubscriptionTest(TestCase):

    def test__get_reason_for_new_subscription_member_initial(self):
        """Does _get_reason_for_new_subscription work for an initial member sub?
        """
        self.assertEqual(
            Subscription._get_reason_for_new_subscription(
                InstitutionFactory(is_member=True)),
            'member_registration')

    def test__get_reason_for_new_subscription_nonmember_initial(self):
        """Does _get_reason_for_new_subscription work for initial nonmember sub?
        """
        self.assertEqual(
            Subscription._get_reason_for_new_subscription(InstitutionFactory()),
            'nonmember_registration')

    def test__get_reason_for_new_subscription_member_renewal(self):
        """Does _get_reason_for_new_subscription work for a member renewal?
        """
        subscription = SubscriptionFactory(
            institution=InstitutionFactory(is_member=True))
        self.assertEqual(
            Subscription._get_reason_for_new_subscription(
                subscription.institution),
            'member_renewal')

    def test__get_reason_for_new_subscription_nonmember_renewal(self):
        """Does _get_reason_for_new_subscription work for a nonmember renewal?
        """
        subscription = SubscriptionFactory()
        self.assertEqual(Subscription._get_reason_for_new_subscription(
            subscription.institution),
            'nonmember_renewal')

    def test__get_start_date_for_new_subscription_lapsed_subscription(self):
        """Does _get_start_date_for_new_subscription work when sub is lapsed?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.'
                      'get_last_subscription_end',
                      lambda x : date.today() - timedelta(days=200))
            start_date = Subscription._get_start_date_for_new_subscription(
                InstitutionFactory())
        self.assertEqual(start_date, date.today())

    def test__get_start_date_for_new_subscription_current_subscription(self):
        """Does _get_start_date_for_new_subscription work when sub is current?
        """
        DAYS_UNTIL_SUB_EXPIRES = 200
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.institutions.models.Institution.'
                'get_last_subscription_end',
                lambda x : date.today() + timedelta(days=DAYS_UNTIL_SUB_EXPIRES))
            start_date = Subscription._get_start_date_for_new_subscription(
                InstitutionFactory())
        self.assertEqual(
            start_date,
            date.today() + timedelta(days=DAYS_UNTIL_SUB_EXPIRES + 1))

    def test__get_start_date_for_new_subscription_subscription_ends_today(self):
        """Does _get_start_date_for_new_subscription work when sub ends today?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.'
                      'get_last_subscription_end',
                      lambda x : date.today())
            start_date = Subscription._get_start_date_for_new_subscription(
                InstitutionFactory())
        self.assertEqual(start_date, date.today() + timedelta(1))

    def test__subscription_discounted_no_previous_subscription(self):
        """Does _subscription_discounted work when there's no prev subscription?
        """
        self.assertFalse(
            Subscription._subscription_discounted(InstitutionFactory()))

    def test__subscription_discounted_current_subscription(self):
        """Does _subscription_discounted work when a subscription is current?
        """
        subscription = SubscriptionFactory(
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=5))
        self.assertTrue(
            Subscription._subscription_discounted(subscription.institution))

    def test__subscription_discounted_recently_lapsed_subscription(self):
        """Does _subscription_discounted work when subs is recently lapsed?
        """
        subscription = SubscriptionFactory(
            start_date=date.today() - timedelta(days=100),
            end_date=date.today() - timedelta(days=5))
        self.assertTrue(
            Subscription._subscription_discounted(subscription.institution))

    def test__subscription_discounted_long_time_lapsed_subscription(self):
        """Does _subscription_discounted work when a subs lapsed long time ago?
        """
        subscription = SubscriptionFactory(
            start_date=date.today() - timedelta(days=1000),
            end_date=date.today() - timedelta(days=900))
        self.assertFalse(
            Subscription._subscription_discounted(subscription.institution))

    def test__apply_promo_code_valid_promo_code(self):
        """Does _apply_promo_code work for a valid promo code?
        """
        promo_code = 'MOTHER-IN-LAW SPECIAL'
        promo_amount = 43
        value_discount = ValueDiscount(
            code=promo_code,
            amount=promo_amount,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1))
        value_discount.save()
        initial_price = 5432
        self.assertEqual(Subscription._apply_promo_code(initial_price,
                                                        promo_code),
            initial_price - promo_amount)

    def test__apply_promo_code_expired_promo_code(self):
        """Does _apply_promo_code work for an expired promo code?
        """
        promo_code = 'FEELING LUCKY?'
        promo_amount = 50
        value_discount = ValueDiscount(
            code=promo_code,
            amount=promo_amount,
            start_date=date.today() - timedelta(days=20),
            end_date=date.today() - timedelta(days=10))
        value_discount.save()
        initial_price = 1000
        self.assertEqual(Subscription._apply_promo_code(initial_price,
                                                        promo_code),
            initial_price)

    def test__apply_promo_code_invalid_promo_code(self):
        """Does _apply_promo_code work for an invalid promo code?
        (Where 'invalid' means nonexistant.)
        """
        initial_price = 10
        self.assertEqual(Subscription._apply_promo_code(initial_price,
                                                        'BO-O-O-GUS CODE'),
                         initial_price)

    def test__apply_promo_code_no_promo_code(self):
        """Does _apply_promo_code work when no promo code is supplied?
        """
        initial_price = 10
        self.assertEqual(Subscription._apply_promo_code(initial_price),
                         initial_price)


    def _test__get_price_for_new_subscription(self, is_member, use_promo,
                                              gets_discount):
        """Tests _get_price_for_new_subscription.

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
        if use_promo:
            promo_code = 'WHO SAID THAT?'
            promo_amount = 50
            value_discount = ValueDiscount(
                code=promo_code,
                amount=promo_amount,
                start_date=date.today() - timedelta(days=1),
                end_date=date.today() + timedelta(days=1))
            value_discount.save()
        else:
            promo_code = None

        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Subscription.'
                      '_subscription_discounted',
                      lambda *args : gets_discount)
            price, discounted = Subscription._get_price_for_new_subscription(
                InstitutionFactory(is_member=is_member),
                                   promo_code=promo_code)

        price_check = (Subscription.MEMBER_BASE_PRICE if is_member else
                       Subscription.NONMEMBER_BASE_PRICE)

        if promo_code:
            price_check -= promo_amount

        if gets_discount:
            price_check /= 2

        self.assertEqual(price, price_check)
        if gets_discount:
            self.assertTrue(discounted)
        else:
            self.assertFalse(discounted)

    def test__get_price_for_new_subscription_member_promo_discount(self):
        """Does _get_price... work for member with promo and discount?
        """
        self._test__get_price_for_new_subscription(
            is_member=True, use_promo=True, gets_discount=True)

    def test__get_price_for_new_subscription_nonmember_promo_discount(self):
        """Does _get_price... work for nonmember with promo and discount?
        """
        self._test__get_price_for_new_subscription(
            is_member=False, use_promo=True, gets_discount=True)

    def test__get_price_for_new_subscription_member_no_promo_discount(self):
        """Does _get_price... work for member with no promo and discount?
        """
        self._test__get_price_for_new_subscription(
            is_member=True, use_promo=False, gets_discount=True)

    def test__get_price_for_new_subscription_nonmember_no_promo_discount(self):
        """Does _get_price... work for nonmember with no promo and discount?
        """
        self._test__get_price_for_new_subscription(
            is_member=False, use_promo=False, gets_discount=True)

    def test__get_price_for_new_subscription_member_no_promo_no_discount(self):
        """Does _get_price... work for member with no promo and no discount?
        """
        self._test__get_price_for_new_subscription(
            is_member=True, use_promo=False, gets_discount=False)

    def test__get_price_for_new_subscription_nonmember_no_promo_no_discount(
            self):
        """Does _get_price... work for nonmember with no promo and no discount?
        """
        self._test__get_price_for_new_subscription(
            is_member=False, use_promo=False, gets_discount=False)

    def test__get_price_for_new_subscription_member_promo_no_discount(self):
        """Does _get_price... work for member with promo and no discount?
        """
        self._test__get_price_for_new_subscription(
            is_member=True, use_promo=True, gets_discount=False)

    def test__get_price_for_new_subscription_nonmember_promo_no_discount(self):
        """Does _get_price... work for nonmember with promo and no discount?
        """
        self._test__get_price_for_new_subscription(
            is_member=False, use_promo=True, gets_discount=False)
