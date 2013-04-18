from datetime import date, timedelta
import unittest

from django.core.exceptions import ValidationError

from stars.apps.registration.models import get_current_discount
from stars.test_factories import ValueDiscountFactory


class ValueDiscountTest(unittest.TestCase):

    def test_both_amount_and_percentage_disallowed(self):
        """Can a ValueDiscount have both an amount and a percentage?
        """
        with self.assertRaises(ValidationError):
            _ = ValueDiscountFactory(amount=10,
                                     percentage=10)

    def test_either_amount_or_percentage_required(self):
        """Can a ValueDiscount have neither an amount nor a percentage?
        """
        with self.assertRaises(ValidationError):
            _ = ValueDiscountFactory(amount=0,
                                     percentage=0)

    def test_amount_only_allowed(self):
        """Can we save a ValueDiscount with just an amount (and no percentage)?
        """
        _ = ValueDiscountFactory(amount=10,
                                 percentage=0)

    def test_percentage_only_allowed(self):
        """Can we save a ValueDiscount with just a percentage (and no amount)?
        """
        _ = ValueDiscountFactory(amount=0,
                                 percentage=10)

    def test_percentage_must_not_be_more_than_100(self):
        """Can percentage be > 100?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(amount=0,
                                 percentage=101)

    def test_start_date_equals_end_date(self):
        """Can start date equal end date?"""
        # Just check that a ValidationError isn't raised:
        _ = ValueDiscountFactory(start_date=date.today(),
                                 end_date=date.today())

    def test_start_date_before_end_date(self):
        """Can start date be before end date?"""
        with self.assertRaises(ValidationError):
            _ = ValueDiscountFactory(
                start_date=date.today(),
                end_date=date.today() - timedelta(days=10))


class ModelsTopLevelTest(unittest.TestCase):

    def test_get_current_discount(self):
        """Does get_current_discounts work?
        """
        raise NotImplemented
    #     exception = None
    #     try:
    #         current_discounts = [
    #             ValueDiscountFactory(
    #                 start_date=date.today() - timedelta(days=10),
    #                 end_date=date.today() + timedelta(days=10)),
    #             ValueDiscountFactory(
    #                 start_date=date.today(),
    #                 end_date=date.today() + timedelta(days=1)),
    #             ValueDiscountFactory(start_date=date.today(),
    #                                  end_date=date.today())
    #         ]
    #         expired_discounts = [
    #             ValueDiscountFactory(
    #                 start_date=date.today() - timedelta(days=10),
    #                 end_date=date.today() - timedelta(days=10)),
    #             ValueDiscountFactory(
    #                 start_date=date.today() - timedelta(days=10),
    #                 end_date=date.today() - timedelta(days=1))
    #         ]
    #         future_discounts = [
    #             ValueDiscountFactory(
    #                 start_date=date.today() + timedelta(days=10),
    #                 end_date=date.today() + timedelta(days=10)),
    #             ValueDiscountFactory(
    #                 start_date=date.today() + timedelta(days=10),
    #                 end_date=date.today() + timedelta(days=100))
    #         ]
    #         self.assertListEqual(list(get_current_discounts()),
    #                              current_discounts)
    #     except Exception as exception:
    #         pass

    #     for discount_list in (current_discounts,
    #                           expired_discounts,
    #                           future_discounts):
    #         for discount in discount_list:
    #             discount.delete()

    #     if exception:
    #         raise exception

    # def test_get_current_discounts_no_current_discounts(self):
    #     """Is get_current_discounts OK when there are are no current discounts?
    #     """
    #     exception = None
    #     try:
    #         discounts = [
    #             ValueDiscountFactory(
    #                 start_date=date.today() - timedelta(days=10),
    #                 end_date=date.today() - timedelta(days=1)),
    #             ValueDiscountFactory(
    #                 start_date=date.today() - timedelta(days=10),
    #                 end_date=date.today() - timedelta(days=1))
    #         ]
    #         self.assertListEqual(list(get_current_discounts()),
    #                              [])
    #     except Exception as exception:
    #         pass
    #     for discount in discounts:
    #         discount.delete()
    #     if exception:
    #         raise exception

    # def test_get_current_discounts_no_discounts(self):
    #     """Is get_current_discounts OK when there are are no discounts?
    #     """
    #     self.assertListEqual(list(get_current_discounts()),
    #                          [])
