"""Tests for CreditUserSubmission.
"""
from django.test import TestCase

from stars.apps.submissions.models import (CreditUserSubmission,
                                           RATED_SUBMISSION_STATUS)
from stars.test_factories import (CreditUserSubmissionFactory,
                                  DocumentationFieldFactory,
                                  DocumentationFieldSubmissionFactory)
import testfixtures


class CreditUserSubmissionTest(TestCase):

    def ten_documentation_fields(self,
                                  credit):
        documentation_fields = []
        for i in xrange(10):
            documentation_field = DocumentationFieldFactory(
                credit=credit)
            documentation_field.save()
            documentation_fields.append(
                documentation_field)
            documentation_field.save()  # so pk is set
        return documentation_fields

    def test_get_documentation_fields(self):
        credit_user_submission = CreditUserSubmissionFactory()

        documentation_fields = self.ten_documentation_fields(
            credit=credit_user_submission.credit)
        
        # # only submissions from rated submissionsets are shown, so
        # # we'll mark this one rated:
        # submissionset = credit_user_submission.get_submissionset()
        # submissionset.status = RATED_SUBMISSION_STATUS

        self.assertItemsEqual(
            documentation_fields,
            credit_user_submission.get_documentation_fields())

    def test_get_documentation_field_submissionss(self):
        credit_user_submission = CreditUserSubmissionFactory()

        # make 10 DocumentationFields:
        documentation_fields = self.ten_documentation_fields(
            credit=credit_user_submission.credit)

        # make a DocumentationFieldSubmission for 5 of those:
        documentation_field_submissions = []
        for i in xrange(len(documentation_fields)):
            if i % 2:
                documentation_field_submission = (
                    DocumentationFieldSubmissionFactory(
                        credit_submission=credit_user_submission,
                        documentation_field=documentation_fields[i]))
                documentation_field_submissions.append(
                    documentation_field_submission)

        self.assertItemsEqual(
            documentation_field_submissions,
            credit_user_submission.get_documentation_field_submissions())


class MockCredit(object):

    def execute_formula(self, *args, **kwargs):
        return (False, None, None, None)
