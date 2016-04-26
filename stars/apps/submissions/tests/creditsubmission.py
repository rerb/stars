"""Tests for apps.submissions.models.CreditSubmission.
"""
from unittest import TestCase

import testfixtures

from stars.apps.credits.models import Credit
from stars.apps.submissions.models import CreditSubmission
from stars.test_factories import (CreditTestSubmissionFactory,
                                  CreditUserSubmissionFactory)


class CreditSubmissionTest(TestCase):

    def test_round_points_logging(self):
        """Does round_points log an error when there's an exception?
        """
        with testfixtures.LogCapture('stars') as log:
            CreditSubmission.round_points(points='bob', log_error=True)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'Error converting formula'))

    def test_validate_points_logging(self):
        """Does validate_points log an error when there's an exception?
        """
        creditsubmission = CreditSubmission()
        creditsubmission.credit = Credit(point_value=10)
        with testfixtures.LogCapture('stars') as log:
            creditsubmission.validate_points(points=-1.0, log_error=True)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'Points (-1.0) are out of range'))

    def test_is_test_true_for_test_submission(self):
        """Is is_test True for a CreditTestSubmission?
        """
        test_submission = CreditTestSubmissionFactory()
        self.assertTrue(test_submission.is_test())

    def test_is_test_false_for_user_submission(self):
        """Is is_test True for a CreditUserSubmission?
        """
        user_submission = CreditUserSubmissionFactory()
        self.assertFalse(user_submission.is_test())
