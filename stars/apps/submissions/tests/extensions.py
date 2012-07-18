"""
    Submission Extension Logic

    Test Premises:
     - 60 days before deadline
     - registered before 2011
     - status
     - max extensions
"""
from django.test import TestCase
from stars.apps.submissions.models import SubmissionSet, MAX_EXTENSIONS

import sys, datetime

class ExtensionTest(TestCase):
    fixtures = ['manager_test.json',]

    def setUp(self):
        pass

    def test60days(self):
        """
            Ensure that no SubmissionSet can be extended before the 60 day deadline
        """

        ss = SubmissionSet.objects.get(pk=1) # deadline 2011-05-1

        today = datetime.date(year=2011, month=3, day=1)
        self.assertFalse(ss.can_apply_for_extension(today=today))

        today = datetime.date(year=2011, month=3, day=2)
        self.assertTrue(ss.can_apply_for_extension(today=today))

        today = datetime.date(year=2011, month=3, day=3)
        self.assertTrue(ss.can_apply_for_extension(today=today))

        today = datetime.date(year=2011, month=3, day=4)
        self.assertTrue(ss.can_apply_for_extension(today=today))
