from datetime import date, timedelta
import unittest

from django.core.exceptions import ValidationError

from .. import models
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

    def test_get_current_discount_errors_for_invalid_code(self):
        """Does get_current_discount raise an error for an invalid code?"""
        with self.assertRaises(models.InvalidDiscountCodeError):
            models.get_current_discount("it didn't look poisonous")

    def test_get_current_discount_errors_for_expired_code(self):
        """Does get_current_discount raise an error for an expired code?"""
        code = "it looked fetal"
        _ = ValueDiscountFactory(code=code,
                                 start_date="1960-02-18",
                                 end_date="1969-06-20")
        with self.assertRaises(models.ExpiredDiscountCodeError):
            models.get_current_discount(code=code)

    def test_get_current_discount_works_for_valid_unexpired_code(self):
        """Does get_current_discount work for a valid, unexpired code?"""
        code = "jimmy cracked corn ain't 'e?"
        value_discount = ValueDiscountFactory(code=code)
        self.assertIsNotNone(models.get_current_discount(code=code))
