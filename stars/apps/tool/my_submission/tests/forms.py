"""Tests for stars.apps.tool.my_submission.forms.
"""
from django.test import TestCase
import testfixtures

from stars.apps.credits.models import DocumentationField
from stars.apps.submissions.models import CreditSubmission, TextSubmission
from stars.apps.tool.my_submission import forms


class NumericSubmissionFormTest(TestCase):

    def test_clean_value_logging(self):
        """Does clean_value log a message if there's no self(.instance)?
        """
        numeric_submission_form = forms.NumericSubmissionForm()
        numeric_submission_form.cleaned_data = {'value': None}
        numeric_submission_form.instance = None

        with testfixtures.LogCapture('stars') as log:
            numeric_submission_form.clean_value()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'INFO')
        self.assertTrue(log.records[0].module_path.startswith('stars'))
        self.assertTrue('No Instance' in log.records[0].msg)


class TextSubmissionFormTest(TestCase):

    def test_clean_value_logging(self):
        """Does clean_value log a message if there's no self(.instance)?
        """
        text_submission = TextSubmission()
        text_submission.documentation_field = DocumentationField()
        text_submission.credit_submission = CreditSubmission()

        text_submission_form = forms.TextSubmissionForm(instance=text_submission)
        text_submission_form.cleaned_data = {'value': None}
        text_submission_form.instance = None

        with testfixtures.LogCapture('stars') as log:
            text_submission_form.clean_value()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'INFO')
        self.assertTrue(log.records[0].module_path.startswith('stars'))
        self.assertTrue('No Instance' in log.records[0].msg)


class LongTextSubmissionFormTest(TestCase):

    def test_clean_value_logging(self):
        """Does clean_value log a message if there's no self(.instance)?
        """
        long_text_submission_form = forms.LongTextSubmissionForm()
        long_text_submission_form.cleaned_data = {'value': None}
        long_text_submission_form.instance = None

        with testfixtures.LogCapture('stars') as log:
            long_text_submission_form.clean_value()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'INFO')
        self.assertTrue(log.records[0].module_path.startswith('stars'))
        self.assertTrue('No Instance' in log.records[0].msg)
