"""Tests for apps.institutions.models.Subscription.
"""
from datetime import date, timedelta
import sys
if sys.version < '2.7':
    from django.utils.unittest import TestCase
else:
    from unittest import TestCase

import testfixtures

from stars.apps.institutions.models import Subscription, SUBSCRIPTION_DURATION
from stars.apps.registration.models import DiscountManager, ValueDiscount
from stars.test_factories import (InstitutionFactory, SubscriptionFactory,
                                  ValueDiscountFactory)


class SubscriptionTest(TestCase):

    def setUp(self):
        self.subscription = SubscriptionFactory(
            institution=InstitutionFactory())
        self.member = InstitutionFactory(is_member=True)
        self.nonmember = InstitutionFactory(is_member=False)

    def test__apply_standard_discount(self):
        price = 10000
        self.assertLess(self.subscription._apply_standard_discount(price),
                        price)

    #################################
    # _calculate_reason() tests:
    #################################

    def test__calculate_reason_member_initial(self):
        """Does _calculate_reason work for an initial member subscription?
        """
        self.subscription.institution = self.member
        self.assertEqual(self.subscription._calculate_reason(),
                         'member_registration')

    def test__calculate_reason_nonmember_initial(self):
        """Does _calculate_reason work for initial nonmember subscription?
        """
        self.subscription.institution = self.nonmember
        self.assertEqual(self.subscription._calculate_reason(),
                         'nonmember_registration')

    def test__calculate_reason_member_renewal(self):
        """Does _calculate_reason work for a member renewal?
        """
        self.subscription.institution = self.member
        self.subscription.save()
        new_subscription = SubscriptionFactory(institution=self.member)
        self.assertEqual(new_subscription._calculate_reason(),
                         'member_renewal')

    def test__calculate_reason_nonmember_renewal(self):
        """Does _calculate_reason work for a nonmember renewal?
        """
        self.subscription.institution = self.nonmember
        self.subscription.save()
        new_subscription = SubscriptionFactory(institution=self.nonmember)
        self.assertEqual(new_subscription._calculate_reason(),
                         'nonmember_renewal')

    ################################
    # calculate_start_date() tests:
    ################################

    def test__calculate_start_date_lapsed_subscription(self):
        """Does _calculate_start_date work when subscription is lapsed?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Subscription.'
                      '_get_latest_subscription_end',
                      lambda x : date.today() - timedelta(days=200))
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
                lambda x : date.today() + timedelta(days=DAYS_UNTIL_SUB_EXPIRES))
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
                      lambda x : date.today())
            start_date = self.subscription._calculate_start_date()
        self.assertEqual(start_date, date.today() + timedelta(1))

    ####################################
    # _subscription_discounted() tests:
    ####################################

    def test__subscription_discounted_no_previous_subscription(self):
        """Does _subscription_discounted work when there's no prev subscription?
        """
        self.assertFalse(self.subscription._subscription_discounted())

    def test__subscription_discounted_current_subscription(self):
        """Does _subscription_discounted work when a subscription is current?
        """
        current_start_date = date.today() - timedelta(days=5)
        current_end_date = date.today() + timedelta(days=5)
        SubscriptionFactory(institution=self.subscription.institution,
                            start_date=current_start_date,
                            end_date=current_end_date)
        self.assertTrue(self.subscription._subscription_discounted())

    def test__subscription_discounted_recently_lapsed_subscription(self):
        """Does _subscription_discounted work when subs is recently lapsed?
        """
        lapsed_start_date = date.today() - timedelta(days=100)
        lapsed_end_date = date.today() - timedelta(days=5)
        SubscriptionFactory(institution=self.subscription.institution,
                            start_date=lapsed_start_date,
                            end_date=lapsed_end_date)
        self.assertTrue(self.subscription._subscription_discounted())

    def test__subscription_discounted_long_time_lapsed_subscription(self):
        """Does _subscription_discounted work when a subs lapsed long time ago?
        """
        lapsed_start_date = date.today() - timedelta(days=1000)
        lapsed_end_date = date.today() - timedelta(days=900)
        SubscriptionFactory(institution=self.subscription.institution,
                            start_date=lapsed_start_date,
                            end_date=lapsed_end_date)
        self.assertFalse(self.subscription._subscription_discounted())

    #############################
    # _apply_promo_code() tests:
    #############################

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
        self.assertEqual(
            self.subscription._apply_promo_code(initial_price,
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
        self.assertEqual(self.subscription._apply_promo_code(initial_price,
                                                             promo_code),
                         initial_price)

    def test__apply_promo_code_invalid_promo_code(self):
        """Does _apply_promo_code work for an invalid promo code?
        (Where 'invalid' means nonexistant.)
        """
        initial_price = 10
        self.assertEqual(self.subscription._apply_promo_code(initial_price,
                                                             'BO-O-O-GUS CODE'),
                         initial_price)

    def test__apply_promo_code_no_promo_code(self):
        """Does _apply_promo_code work when no promo code is supplied?
        """
        initial_price = 10
        self.assertEqual(self.subscription._apply_promo_code(initial_price),
                         initial_price)

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

        self.subscription._subscription_discounted = (
            lambda *args : gets_discount)

        price, promo_discount_applied = self.subscription.calculate_price(
            promo_code=promo_code)

        price_check = (Subscription.MEMBER_BASE_PRICE if is_member else
                       Subscription.NONMEMBER_BASE_PRICE)

        if promo_code:
            price_check -= promo_amount

        if gets_discount:
            price_check = self.subscription._apply_standard_discount(
                price_check)

        self.assertEqual(price, price_check)

        if DiscountManager().is_code_current(promo_code):
            self.assertTrue(promo_discount_applied)
        else:
            self.assertFalse(promo_discount_applied)

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
        (subscription, promo_code_applied) = Subscription.create(
            institution=InstitutionFactory())
        self.assertEqual(subscription.id, None)

    def test_create_with_promo_code(self):
        """Does create() work when a promo code is supplied?"""
        promo = ValueDiscountFactory(
            start_date=date.today(),
            end_date=date.today() + timedelta(days=100),
            amount=10)
        (subscription, promo_code_applied) = Subscription.create(
            institution=InstitutionFactory(),
            promo_code=promo.code)
        self.assertTrue(promo_code_applied)

    def test_create_without_promo_code(self):
        """Does create() work when a promo code is not supplied?"""
        (subscription, promo_code_applied) = Subscription.create(
            institution=InstitutionFactory())
        self.assertFalse(promo_code_applied)

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


    # def test__calculate_date_range(self):
    #     raise NotImplemented

    # def test__get_latest_subscription(self):
    #     raise NotImplemented

    # def test__get_latest_subscription_end(self):
    #     raise NotImplemented

    # def test_get_available_ratings(self):
    #     raise NotImplemented

    # def test_purchase(self):
    #     raise NotImplemented

    # def test_pay(self):
    #     raise NotImplemented

    # def test__send_post_purchase_email(self):
    #     raise NotImplemented

    # def test__update_instituion_after_purchase(self):
    #     raise NotImplemented

    # def test__send_post_purchase_pay_now_email(self):
    #     raise NotImplemented

    # def test__send_post_purchase_pay_later_email(self):
    #     raise NotImplemented

    # def test__send_email(self):
    #     raise NotImplemented

    # def test__send_post_purchase_executive_renewal_email(self):
    #     raise NotImplemented
