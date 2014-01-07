"""Tests for apps.credits.models.Unit.
"""
from django.test import TestCase

from stars.apps.credits.models import Unit


class UnitTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(UnitTest, self).__init__(*args, **kwargs)
        self.unit = Unit()

    def test_ratio_cannot_be_None(self):
        """Is Unit.ratio == None disallowed?"""
        self.unit.ratio = None
        self.assertRaises(Exception, self.unit.save)

    def test_ratio_cannot_be_zero(self):
        """Is Unit.ratio == 0 disallowed?"""
        self.unit.ratio = 0
        self.assertRaises(Exception, self.unit.save)

    def test_revert_is_reverse_of_convert(self):
        """Is Unit.revert() the reverse of Unit.convert()?"""
        self.unit.ratio = 3.3
        self.unit.save()
        amount = 10
        self.assertEqual(amount,
                         self.unit.revert(self.unit.convert(amount)))

    def test_convert_is_reverse_of_revert(self):
        """Is Unit.convert() the reverse of Unit.revert()?"""
        self.unit.ratio = 3.3
        self.unit.save()
        amount = 10
        self.assertEqual(amount,
                         self.unit.convert(self.unit.revert(amount)))
