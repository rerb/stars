"""Tests for apps.submissions.models.DocumentationFieldSubmission that
maps to a DocumentationField of type "calculated".
"""
from unittest import TestCase

from stars.test_factories import (CreditUserSubmissionFactory,
                                  DocumentationFieldFactory)
from stars.apps.submissions.models import NumericSubmission


class CalculatedFieldTest(TestCase):

    def setUp(self):
        credit_user_submission = CreditUserSubmissionFactory()
        credit = credit_user_submission.credit
        numeric_field = DocumentationFieldFactory(credit=credit,
                                                  type="numeric")
        calculated_field = DocumentationFieldFactory(credit=credit,
                                                     type="calculated",
                                                     formula="value = A * 10")

        self.calculated_submission = NumericSubmission.objects.create(
            documentation_field=calculated_field,
            credit_submission=credit_user_submission,
            value=999)

        self.numeric_submission = NumericSubmission.objects.create(
            documentation_field=numeric_field,
            credit_submission=credit_user_submission,
            value=0)

    def test_save_of_calculated_field(self):
        """Does saving a calculated field change its value?
        It shouldn't.
        """
        self.calculated_submission.save()
        fresh_calculated_submission = NumericSubmission.objects.get(
            id=self.calculated_submission.id)
        self.assertEqual(999, fresh_calculated_submission.value)

    def test_save_of_noncalculated_field(self):
        """Does saving a noncalculated field change a related calculated field?
        It should.
        """
        self.numeric_submission.value = 10
        self.numeric_submission.save()
        fresh_calculated_submission = NumericSubmission.objects.get(
            id=self.calculated_submission.id)
        self.assertEqual(100, fresh_calculated_submission.value)
