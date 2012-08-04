"""Tests for apps.credits.models.CreditSet.
"""
from unittest import TestCase

import testfixtures

from stars.apps.credits.models import CreditSet


class CreditsetTest(TestCase):

    def setUp(self):
        self.creditset = CreditSet()

    def test_get_rating_logging(self):
        """Does get_rating log an error when there's no rating?
        """
        with testfixtures.LogCapture('stars') as log:
            self.creditset.get_rating(None)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].module_path.startswith('stars'))
        self.assertTrue('No valid rating' in log.records[0].msg)
