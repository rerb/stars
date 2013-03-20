"""Tests for CreditUserSubmission.
"""
from django.test import TestCase

from stars.apps.submissions.models import CreditUserSubmission
import testfixtures


class CreditUserSubmissionTest(TestCase):

    fixtures = ['creditusersubmission.json']

    def test__calculate_points_error_logging(self):
        """Does _calculate_points log an error message when it should?
        """
        credit_user_submission = CreditUserSubmission.objects.get(pk=1)
        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.submissions.models.CreditUserSubmission.'
                          'is_complete',
                          lambda x: True)
                r.replace('stars.apps.submissions.models.CreditUserSubmission.'
                          'credit',
                          MockCredit())
                credit_user_submission._calculate_points()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'There was an error processing this credit'))


class MockCredit(object):

    def execute_formula(self, *args, **kwargs):
        return (False, None, None, None)
