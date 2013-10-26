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
            ValueDiscountFactory(amount=10, percentage=10)

    def test_either_amount_or_percentage_required(self):
        """Can a ValueDiscount have neither an amount nor a percentage?
        """
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(amount=0, percentage=0)

    def test_amount_only_allowed(self):
        """Can we save a ValueDiscount with just an amount (and no percentage)?
        """
        value_discount = ValueDiscountFactory(amount=10,
                                              percentage=0)
        value_discount.save()

    def test_percentage_only_allowed(self):
        """Can we save a ValueDiscount with just a percentage (and no amount)?
        """
        value_discount = ValueDiscountFactory(amount=0,
                                              percentage=10)
        value_discount.save()

    def test_percentage_must_not_be_more_than_100(self):
        """Can percentage be > 100?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(amount=0, percentage=101)

    def test_start_date_equals_end_date(self):
        """Can start date equal end date?"""
        # Just check that a ValidationError isn't raised:
        value_discount = ValueDiscountFactory(start_date=date.today(),
                                              end_date=date.today())
        value_discount.save()

    def test_start_date_before_end_date(self):
        """Can start date be before end date?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(start_date=date.today(),
                                 end_date=date.today() - timedelta(days=10))


class AutomaticDiscountTest(unittest.TestCase):

    def setUp(self):
        """Create an AutomaticDiscount that started ten days ago
        and ends ten days from today.
        """
        models.ValueDiscount.objects.all().delete()
        self.other_auto_disc = ValueDiscountFactory(
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=10),
            automatic=True)
        self.other_auto_disc.save()
        
    def test__overlapping_automatic_discount_same_start_date(self):
        """Does _overlapping_automatic_discount handle same start date?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(
                start_date=self.other_auto_disc.start_date,
                end_date=self.other_auto_disc.end_date - timedelta(days=5),
                automatic=True)

    def test__overlapping_automatic_discount_same_end_date(self):
        """Does _overlapping_automatic_discount handle same end date?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(
                start_date=(self.other_auto_disc.start_date -
                            timedelta(days=5)),
                end_date=self.other_auto_disc.end_date,
                automatic=True)

    def test__overlapping_automatic_discount_same_date_range(self):
        """Does _overlapping_automatic_discount handle same date range?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(
                start_date=self.other_auto_disc.start_date,
                end_date=self.other_auto_disc.end_date,
                automatic=True)

    def test__overlapping_automatic_discount_start_date_overlap(self):
        """Does _overlapping_automatic_discount handle start date overlap?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(
                start_date=(self.other_auto_disc.start_date +
                            timedelta(days=5)),
                end_date=self.other_auto_disc.end_date + timedelta(days=5),
                automatic=True)

    def test__overlapping_automatic_discount_end_date_overlap(self):
        """Does _overlapping_automatic_discount handle end date overlap?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(
                start_date=(self.other_auto_disc.start_date -
                            timedelta(days=5)),
                end_date=self.other_auto_disc.end_date - timedelta(days=5),
                automatic=True)

    def test__overlapping_automatic_discount_contains_another(self):
        """Does _overlapping_automatic_discount handle this inside another?
        """
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(
                start_date=(self.other_auto_disc.start_date -
                            timedelta(days=5)),
                end_date=self.other_auto_disc.end_date + timedelta(days=5),
                automatic=True)

    def test__overlapping_automatic_discount_end_date_eq_other_start_date(
            self):
        """Does _overl.._auto.._disc.. handle end date == other start date?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(
                start_date=(self.other_auto_disc.start_date -
                            timedelta(days=5)),
                end_date=self.other_auto_disc.start_date,
                automatic=True)

    def test__overlapping_automatic_discount_start_date_eq_other_end_date(
            self):
        """Does _overl.._auto.._disc.. handle start date == other end date?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(
                start_date=self.other_auto_disc.end_date,
                end_date=self.other_auto_disc.end_date + timedelta(days=5),
                automatic=True)

    def test__overlapping_automatic_discount_inside_another(self):
        """Does _overl.._auto.._disc.. handle other discount inside this one?
        """
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(
                start_date=(self.other_auto_disc.start_date +
                            timedelta(days=5)),
                end_date=self.other_auto_disc.end_date - timedelta(days=5),
                automatic=True)

    def test__overlapping_automatic_discount_no_overlap(self):
        """Does _overl.._auto.._disc.. handle no overlap?"""
        automatic_discount = ValueDiscountFactory(
            start_date=self.other_auto_disc.end_date + timedelta(days=5),
            end_date=self.other_auto_disc.end_date + timedelta(days=10),
            automatic=True)
        self.assertTrue(automatic_discount.discount_applies())

    def test_clean_no_amount_or_percentage(self):
        """Does clean reject if there's no amount or percentage?"""
        with self.assertRaises(ValidationError):
            ValueDiscountFactory(amount=None, 
                                 percentage=None,
                                 automatic=True)

    def test_discount_applies_with_no_applicability_filter(self):
        """Is discount_applies() True when applicability_filter is blank?
        """
        self.other_auto_disc.applicability_filter = ''
        self.assertTrue(self.other_auto_disc.discount_applies())

    def test_discount_applies_with_bad_syntax_in_applicability_filter(self):
        """Is discount_applies() False when applicability_filter is garbage?
        """
        self.other_auto_disc.applicability_filter = 'bo-o-o-o-gus'
        self.assertFalse(self.other_auto_disc.discount_applies())

    def test_discount_applies_with_true_applicability_filter(self):
        """Is discount_applies() True when applicability_filter is True?
        """
        self.other_auto_disc.applicability_filter = 'True'
        self.assertTrue(self.other_auto_disc.discount_applies())

    def test_discount_applies_with_false_applicability_filter(self):
        """Is discount_applies() False when applicability_filter is False?
        """
        self.other_auto_disc.applicability_filter = 'False'
        self.assertFalse(self.other_auto_disc.discount_applies())

    def test_applicability_filter_can_access_extra_locals(self):
        """Can applicability_filter access a value in extra_locals?
        """
        self.other_auto_disc.applicability_filter = (
            "locals()['new_local'] == 1")
        self.assertTrue(self.other_auto_disc.discount_applies(
            extra_locals={'new_local': 1}))

    def test_applicability_filter_can_access_extra_globals(self):
        """Can applicability_filter access a value in extra_globals?
        """
        self.other_auto_disc.applicability_filter = (
            "globals()['new_global'] == 1")
        self.assertTrue(self.other_auto_disc.discount_applies(
            extra_globals={'new_global': 1}))


class ModelsTopLevelTest(unittest.TestCase):

    def setUp(self):
        models.ValueDiscount.objects.all().delete()

    def test_get_current_discount_errors_for_invalid_code(self):
        """Does get_current_discount raise an error for an invalid code?"""
        with self.assertRaises(models.InvalidDiscountCodeError):
            models.get_current_discount("it didn't look poisonous")

    def test_get_current_discount_errors_for_expired_code(self):
        """Does get_current_discount raise an error for an expired code?"""
        code = "it looked fetal"
        expired_discount = ValueDiscountFactory(code=code,
                                                start_date="1960-02-18",
                                                end_date="1969-06-20")
        expired_discount.save()
        with self.assertRaises(models.ExpiredDiscountCodeError):
            models.get_current_discount(code=code)

    def test_get_current_discount_works_for_valid_unexpired_code(self):
        """Does get_current_discount work for a valid, unexpired code?"""
        code = "jimmy cracked corn ain't 'e?"
        current_discount = ValueDiscountFactory(code=code)
        current_discount.save()
        self.assertIsNotNone(models.get_current_discount(code=code))

    def test_get_automatic_discount_errors_for_expired_discount(self):
        """Does get_automatic_discount raise an error for an expired code?
        """
        expired_discount = ValueDiscountFactory(start_date="1960-02-18",
                                                    end_date="1969-06-20",
                                                    automatic=True)
        expired_discount.save()
        with self.assertRaises(models.NoActiveAutomaticDiscountError):
            models.get_automatic_discount()

    def test_get_automatic_discount_works_for_unexpired_discount(self):
        """Does get_automatic_discount work for an unexpired discount?"""
        current_discount = ValueDiscountFactory(
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=10),
            automatic=True)
        current_discount.save()
        self.assertEquals(models.get_automatic_discount().id,
                          current_discount.id)

    def test_get_automatic_discount_errors_for_garbage_applicability_filter(
            self):
        """Does get_.._discount error when applicability_filter is garbage?
        """
        current_discount = ValueDiscountFactory(
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() + timedelta(days=10),
            applicability_filter='bo-o-o=o=o=gus',
            automatic=True)
        current_discount.save()
        with self.assertRaises(models.NoActiveAutomaticDiscountError):
            models.get_automatic_discount()

    def test_get_automatic_discount_with_extra_locals(self):
        """Does get_automatic_discount handle extra_locals?"""
        automatic_discount = ValueDiscountFactory(
            applicability_filter="locals()['new_local'] == 1",
            automatic=True)
        automatic_discount.save()
        self.assertEqual(
            models.get_automatic_discount(extra_locals={'new_local': 1}).id,
            automatic_discount.id)

    def test_get_automatic_discount_with_extra_globals(self):
        """Does get_automatic_discount handle extra_globals?"""
        automatic_discount = ValueDiscountFactory(
            applicability_filter="globals()['new_global'] == 1",
            automatic=True)
        automatic_discount.save()
        self.assertEqual(
            models.get_automatic_discount(extra_globals={'new_global': 1}).id,
            automatic_discount.id)
