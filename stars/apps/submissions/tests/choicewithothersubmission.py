"""Tests for apps.submissions.models.ChoiceWithOtherSubmission.
"""
from unittest import TestCase

import testfixtures

from stars.apps.submissions.models import ChoiceWithOtherSubmission


class ChoiceWithOtherSubmissionTest(TestCase):

    def test_decompress_logging(self):
        """Does decompress log an error when there's an exception?
        """
        cwos = ChoiceWithOtherSubmission()
        with testfixtures.LogCapture('stars') as log:
            cwos.decompress(value=-99999)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].module_path.startswith('stars'))
        self.assertTrue(log.records[0].msg.startswith(
            'Attempt to decompress non-existing'))
