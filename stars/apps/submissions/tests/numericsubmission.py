"""Tests for apps.submissions.models.NumericSubmission.
"""
from unittest import TestCase

from stars.test_factories import (CreditFactory,
                                  CreditUserSubmissionFactory,
                                  DocumentationFieldFactory,
                                  NumericSubmissionFactory)
from stars.apps.credits.models import DocumentationField, Unit
from stars.apps.submissions.models import NumericSubmission


class NumericSubmissionTest(TestCase):

    def setUp(self):
        self.us_units = Unit(is_metric=False,
                             ratio=.25)
        self.us_units.save()
        self.metric_units = Unit(is_metric=True,
                                 ratio=4,
                                 equivalent=self.us_units)
        self.metric_units.save()
        self.us_units.equivalent = self.metric_units
        self.us_units.save()

        self.credit_user_submission = CreditUserSubmissionFactory()
        self.documentation_field = DocumentationFieldFactory()

    def set_institution_prefers_metric_system(self, what):
        institution = self.credit_user_submission.get_institution()
        institution.prefers_metric_system = what
        institution.save()

    def test_save_store_us_value_when_using_metric(self):
        """Does save() store US value when using metric?
        """
        self.set_institution_prefers_metric_system(True)
        self.documentation_field.units = self.metric_units
        self.documentation_field.save()

        numeric_submission = NumericSubmission(
            documentation_field=self.documentation_field,
            credit_submission=self.credit_user_submission,
            metric_value=100)

        numeric_submission.save()
        self.assertEqual(400, numeric_submission.value)

    def test_save_store_metric_value_when_not_using_metric(self):
        """Does save() store metric value when not using metric?
        """
        self.set_institution_prefers_metric_system(False)
        self.documentation_field.units = self.us_units
        self.documentation_field.save()

        numeric_submission = NumericSubmission(
            documentation_field=self.documentation_field,
            credit_submission=self.credit_user_submission,
            value=100)

        numeric_submission.save()
        self.assertEqual(25, numeric_submission.metric_value)

    def test_save_handle_metric_value_is_none_using_metric(self):
        """Does save() handle it when the metric_value is None?
        (Using metric system.)
        """
        self.set_institution_prefers_metric_system(True)
        self.documentation_field.units = self.metric_units
        self.documentation_field.save()

        numeric_submission = NumericSubmission(
            documentation_field=self.documentation_field,
            credit_submission=self.credit_user_submission,
            metric_value=None)

        numeric_submission.save()

        self.assertEqual(None, numeric_submission.metric_value)

    def test_save_handle_metric_value_is_none_not_using_metric(self):
        """Does save() handle it when the metric_value is None?
        (Not using metric system.)
        """
        self.set_institution_prefers_metric_system(False)
        self.documentation_field.units = self.us_units
        self.documentation_field.save()

        numeric_submission = NumericSubmission(
            documentation_field=self.documentation_field,
            credit_submission=self.credit_user_submission,
            metric_value=None)

        numeric_submission.save()

        self.assertEqual(None, numeric_submission.metric_value)

    def test_save_handle_value_is_none_using_metric(self):
        """Does save() handle it when the value is None?
        (Using metric system.)
        """
        self.set_institution_prefers_metric_system(True)
        self.documentation_field.units = self.metric_units
        self.documentation_field.save()

        numeric_submission = NumericSubmission(
            documentation_field=self.documentation_field,
            credit_submission=self.credit_user_submission,
            value=None)

        numeric_submission.save()

        self.assertEqual(None, numeric_submission.value)

    def test_save_handle_value_is_none_not_using_metric(self):
        """Does save() handle it when the value is None?
        (Not using metric system.)
        """
        self.set_institution_prefers_metric_system(False)
        self.documentation_field.units = self.us_units
        self.documentation_field.save()

        numeric_submission = NumericSubmission(
            documentation_field=self.documentation_field,
            credit_submission=self.credit_user_submission,
            value=None)

        numeric_submission.save()

        self.assertEqual(None, numeric_submission.value)

    def test_save_without_units_succeeds(self):
        """Is save() ok when the doc field has no units?
        """
        self.documentation_field.units = None
        self.documentation_field.save()

        numeric_submission = NumericSubmission(
            documentation_field=self.documentation_field,
            credit_submission=self.credit_user_submission,
            value=100)

        numeric_submission.save()

        self.assertEqual(100, numeric_submission.value)

    def test_save_without_units_succeeds_using_metric(self):
        """Is save() ok when the doc field has no units and using metric?
        """
        self.set_institution_prefers_metric_system(True)
        self.documentation_field.units = None
        self.documentation_field.save()

        numeric_submission = NumericSubmission(
            documentation_field=self.documentation_field,
            credit_submission=self.credit_user_submission,
            metric_value=100)

        numeric_submission.save()

        self.assertEqual(100, numeric_submission.metric_value)

    def test_calculated_field_is_calculated_when_term_changes(self):
        credit = CreditFactory()
        first_term_field = DocumentationFieldFactory(
            credit=credit,
            type='numeric',
            identifier='AA')
        second_term_field = DocumentationFieldFactory(
            credit=credit,
            type='numeric',
            identifier='AB')
        calculated_field = DocumentationField.objects.create(
            credit=credit,
            type='calculated',
            formula='value = AA + AB')
        credit_submission = CreditUserSubmissionFactory(
            credit=credit)
        first_term_submission = NumericSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=first_term_field,
            value=1)
        NumericSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=second_term_field,
            value=2)
        calculated_submission = NumericSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=calculated_field,
            value=None)

        first_term_submission.value = 10
        first_term_submission.save()

        # We have a dirty read.
        calculated_submission = NumericSubmission.objects.get(
            pk=calculated_submission.pk)

        self.assertEqual(12, calculated_submission.value)

    def test_calculated_field_is_cleared_when_term_goes_invalid(self):
        credit = CreditFactory()
        first_term_field = DocumentationFieldFactory(
            credit=credit,
            type='numeric',
            identifier='BA')
        second_term_field = DocumentationFieldFactory(
            credit=credit,
            type='numeric',
            identifier='BB')
        calculated_field = DocumentationField.objects.create(
            credit=credit,
            type='calculated',
            formula='value = BA + BB')
        credit_submission = CreditUserSubmissionFactory(
            credit=credit)
        first_term_submission = NumericSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=first_term_field,
            value=1)
        NumericSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=second_term_field,
            value=2)
        calculated_submission = NumericSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=calculated_field,
            value=None)

        first_term_submission.value = None
        first_term_submission.save()

        # We have a dirty read.
        calculated_submission = NumericSubmission.objects.get(
            pk=calculated_submission.pk)

        self.assertEqual(None, calculated_submission.value)
