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

    fixtures = ['creditusersubmission.json']

    def test_get_documentation_fields(self):
        credit_user_submission = CreditUserSubmissionFactory()

        # make 10 DocumentationFields:
        test_documentation_fields = [
            DocumentationFieldFactory(credit=credit_user_submission.credit)
            for i in xrange(10)
        ]

        # make a DocumentationFieldSubmission for 5 of those:
        test_documentation_field_submissions = [
            DocumentationFieldSubmissionFactory(
                credit_submission=credit_user_submission,
                documentation_field=test_documentation_fields[i])
            for i in xrange(10)
            if i % 2 == 0
        ]

        # only submissions from rated submissionsets are shown, so
        # we'll mark this one rated:
        submissionset = credit_user_submission.get_submissionset()
        submissionset.status = RATED_SUBMISSION_STATUS
        submissionset.save()

        expected_documentation_fields = [
            documentation_field_submission.documentation_field for
            documentation_field_submission in
            test_documentation_field_submissions
        ]
        import ipdb; ipdb.set_trace()

        self.assertItemsEqual(
            expected_documentation_fields,
            credit_user_submission.get_documentation_fields())


    def test_get_submission_fields(self):
        """get_submission_fields return correct DocumentationFieldSubmissions?
        """
        credit_user_submission = CreditUserSubmissionFactory()

        # make 10 DocumentationFields:
        test_documentation_fields = [
            DocumentationFieldFactory(credit=credit_user_submission.credit)
            for i in xrange(10)
        ]

        # make a DocumentationFieldSubmission for 5 of those:
        test_documentation_field_submissions = [
            DocumentationFieldSubmissionFactory(
                credit_submission=credit_user_submission,
                documentation_field=test_documentation_fields[i])
            for i in xrange(10)
            if i % 2 == 0
        ]

        self.assertItemsEqual(
            test_documentation_field_submissions,
            credit_user_submission.get_submission_fields())


class MockCredit(object):

    def execute_formula(self, *args, **kwargs):
        return (False, None, None, None)
