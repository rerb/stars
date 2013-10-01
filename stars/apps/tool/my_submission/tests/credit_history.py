"""Tests for apps.tool.my_submission.credit_history_tab."""
from django.test import TestCase

from stars.apps.credits import models as credits_models
from stars.apps.submissions import models as submissions_models
from stars.test_factories import (CreditFactory,
                                  DocumentationFieldFactory,
                                  DocumentationFieldSubmissionFactory,
                                  InstitutionFactory)

from ..credit_history import (get_doc_field_history,
                              get_doc_field_submission_history,
                              get_doc_field_submission_history_for_credit,
                              get_doc_field_submission_for_doc_field)


class GetDocFieldHistoryTest(TestCase):

    def setUp(self):
        self.documentation_field = DocumentationFieldFactory()

    def test_no_previous_version(self):
        """Is just the original doc_field returned when there are no prev?
        """
        self.assertItemsEqual(
            get_doc_field_history(self.documentation_field),
            [self.documentation_field])

    def test_one_previous_version(self):
        """Is the only previous version returned?"""
        previous_documentation_field = DocumentationFieldFactory()
        self.documentation_field.previous_version = (
            previous_documentation_field)
        
        self.assertItemsEqual(
            get_doc_field_history(self.documentation_field),
            [self.documentation_field,
             previous_documentation_field])

    def test_many_previous_versions(self):
        """Are all previous versions returned?"""
        second_documentation_field = DocumentationFieldFactory(
            previous_version=self.documentation_field)
        third_documentation_field = DocumentationFieldFactory(
            previous_version=second_documentation_field)
        
        self.assertItemsEqual(
            get_doc_field_history(third_documentation_field),
            [self.documentation_field,
             second_documentation_field,
             third_documentation_field])


class GetDocFieldSubmissionForDocFieldTest(TestCase):
        
    @classmethod
    def setUpClass(cls):
        # One DocumentationFieldSubmission:
        cls.documentation_field_submission = (
            DocumentationFieldSubmissionFactory(value="test"))
        cls.documentation_field = (
            cls.documentation_field_submission.documentation_field)

        # An institution, linked to the submissionset for 
        # the DocumentationFieldSubmission created above:
        cls.institution = InstitutionFactory()        
        submission_set = (
            cls.documentation_field_submission.get_submissionset())
        submission_set.institution = cls.institution
        submission_set.save()

    def test_one_doc_field_submission(self):
        """Is the only DocumentationFieldSubmission returned?"""
        doc_field_submission = get_doc_field_submission_for_doc_field(
            documentation_field=self.documentation_field,
            institution=self.institution)

        self.assertEqual(doc_field_submission,
                         self.documentation_field_submission)

    def test_two_doc_field_submissions(self):
        """Is the correct DocumentationFieldSubmisssion returned?"""
        # Another DocumentationFieldSubmission, unrelated to 
        # self.documentation_field:
        another_documentation_field_submission = (
            DocumentationFieldSubmissionFactory(value="anothertest"))
        
        doc_field_submission = get_doc_field_submission_for_doc_field(
            documentation_field=self.documentation_field,
            institution=self.institution)

        self.assertEqual(doc_field_submission,
                         self.documentation_field_submission)


class GetDocFieldSubmissionHistoryTest(TestCase):

    @classmethod
    def setUpClass(cls):
        # One DocumentationFieldSubmission:
        cls.documentation_field_submission = (
            DocumentationFieldSubmissionFactory(value="Mr. Green Jeans"))
        cls.documentation_field = (
            cls.documentation_field_submission.documentation_field)

        # An institution, linked to the submissionset for 
        # the DocumentationFieldSubmission created above:
        cls.institution = InstitutionFactory()        
        cls.submission_set = (
            cls.documentation_field_submission.get_submissionset())
        cls.submission_set.institution = cls.institution
        cls.submission_set.save()

    def test_no_history(self):
        """Is empty set returned when there's no history?"""
        self.assertEqual(
            get_doc_field_submission_history(
                documentation_field=self.documentation_field,
                institution=self.institution),
            set())

    def test_short_history(self):
        """When there's only one previous version, is it returned?"""
        second_documentation_field = DocumentationFieldFactory(
            credit=self.documentation_field.credit,
            previous_version=self.documentation_field)

        second_documentation_field_submission = (
            DocumentationFieldSubmissionFactory(
                documentation_field=second_documentation_field,
                value="Cap'n Kangaroo"))
        submission_set = (
            second_documentation_field_submission.get_submissionset())
        submission_set.institution = self.institution
        submission_set.status = submissions_models.RATED_SUBMISSION_STATUS
        submission_set.save()

        self.submission_set.status = (
            submissions_models.RATED_SUBMISSION_STATUS)
        self.submission_set.save()
        
        self.assertEqual(
            get_doc_field_submission_history(
                documentation_field=second_documentation_field,
                institution=self.institution),
            set([self.documentation_field_submission]))

    def test_short_migrated_from_history(self):
        """When no previous_versions, are migrated_from values returned?"""
        second_documentation_field = DocumentationFieldFactory(
            credit=self.documentation_field.credit,
            previous_version=self.documentation_field)

        second_documentation_field_submission = (
            DocumentationFieldSubmissionFactory(
                documentation_field=second_documentation_field,
                value="Mr. Rogers"))
        submission_set = (
            second_documentation_field_submission.get_submissionset())
        submission_set.institution = self.institution
        submission_set.migrated_from = self.submission_set
        submission_set.save()

        self.submission_set.status = (
            submissions_models.RATED_SUBMISSION_STATUS)
        self.submission_set.save()
        
        self.assertEqual(
            get_doc_field_submission_history(
                documentation_field=second_documentation_field,
                institution=self.institution),
            set([self.documentation_field_submission]))

    def test_short_unrated_history(self):
        """When there's only one previous UNRATED version, is it returned?"""
        second_documentation_field = DocumentationFieldFactory(
            credit=self.documentation_field.credit,
            previous_version=self.documentation_field)

        second_documentation_field_submission = (
            DocumentationFieldSubmissionFactory(
                documentation_field=second_documentation_field,
                value="Miss Ann"))
        submission_set = (
            second_documentation_field_submission.get_submissionset())
        submission_set.institution = self.institution
        submission_set.save()

        self.assertEqual(
            get_doc_field_submission_history(
                documentation_field=second_documentation_field,
                institution=self.institution),
            set())

    def test_longer_history(self):
        """When there's two previous versions, are they both returned?"""
        second_documentation_field = DocumentationFieldFactory(
            credit=self.documentation_field.credit,
            previous_version=self.documentation_field)
        third_documentation_field = DocumentationFieldFactory(
            credit=self.documentation_field.credit,
            previous_version=second_documentation_field)

        second_documentation_field_submission = (
            DocumentationFieldSubmissionFactory(
                documentation_field=second_documentation_field,
                value="Barney Bean"))
        submission_set = (
            second_documentation_field_submission.get_submissionset())
        submission_set.institution = self.institution
        submission_set.status = (
            submissions_models.RATED_SUBMISSION_STATUS)
        submission_set.save()

        self.submission_set.status = (
            submissions_models.RATED_SUBMISSION_STATUS)
        self.submission_set.save()

        self.assertEqual(
            get_doc_field_submission_history(
                documentation_field=third_documentation_field,
                institution=self.institution),
            set([self.documentation_field_submission,
                 second_documentation_field_submission]))

    def test_rated_and_migrated_from_history(self):
        """Are previous versions and migrated_from values returned?"""

        # 3 doc field submissions
        # self.doc_field is previous version of 2nd doc field
        # 3rd doc field is not linked via previous version,
        # but its submissionset is migrated_from 2nd submission set
        #
        # expect: 2nd and 3rd doc field submissions as history

        # 2nd doc field with orig as prev version:
        second_documentation_field = DocumentationFieldFactory(
            credit=self.documentation_field.credit,
            previous_version=self.documentation_field)

        # doc_field_sub for 2nd doc field:
        second_documentation_field_submission = (
            DocumentationFieldSubmissionFactory(
                documentation_field=second_documentation_field,
                value="Carol Burnett"))

        # 3rd doc field with 2nd as previous version
        third_documentation_field = DocumentationFieldFactory(
            credit=self.documentation_field.credit,
            previous_version=second_documentation_field)

        # doc_field_sub for 3rd doc field:
        third_documentation_field_submission = (
            DocumentationFieldSubmissionFactory(
                documentation_field=third_documentation_field,
                value="Bob Newhart"))

        # first submissionset is rated:
        self.submission_set.status = (
            submissions_models.RATED_SUBMISSION_STATUS)
        self.submission_set.save()

        # 2nd submissionset is rated:
        second_submission_set = (
            second_documentation_field_submission.get_submissionset())
        second_submission_set.institution = self.institution
        second_submission_set.status = (
            submissions_models.RATED_SUBMISSION_STATUS)
        second_submission_set.save()

        # 3rd submissionset is migrated from 2nd (and
        # unrated)
        third_submission_set = (
            third_documentation_field_submission.get_submissionset())
        third_submission_set.institution = self.institution
        third_submission_set.migrated_from = second_submission_set
        third_submission_set.save()
        
        history = get_doc_field_submission_history(
            documentation_field=third_documentation_field,
            institution=self.institution)
        
        self.assertEqual(
            history,
            set([self.documentation_field_submission,
                 second_documentation_field_submission]))


class GetDocFieldSubmissionHistoryForCreditTest(TestCase):

    def setUp(self):
        self.institution = InstitutionFactory()

        # make 3 credits, each with one documentation field:
        self.first_credit = CreditFactory()
        self.second_credit = CreditFactory()
        self.third_credit = CreditFactory()
        
        # a DocumentationField with 2 descendents:
        self.first_documentation_field = DocumentationFieldFactory(
            credit=self.first_credit)
        self.first_documentation_field.save()
        self.second_documentation_field = DocumentationFieldFactory(
            credit=self.second_credit,
            previous_version=self.first_documentation_field)
        self.second_documentation_field.save()
        self.third_documentation_field = DocumentationFieldFactory(
            credit=self.third_credit,
            previous_version=self.second_documentation_field)
        self.third_documentation_field.save()

        # a DocumentationField with no descendents:
        self.dead_end_documentation_field = DocumentationFieldFactory(
            credit=self.first_credit)
        self.dead_end_documentation_field.save()

    def setUpHistory(self):
        """Add some history to the DocumentationFields already
        defined.
        """
        # doc_field_sub for first doc field:
        self.first_documentation_field_submission = (
            DocumentationFieldSubmissionFactory(
                documentation_field=self.first_documentation_field,
                value="Laura Petrie"))
        
        # first submission set is rated:
        first_submission_set = (
            self.first_documentation_field_submission.get_submissionset())
        first_submission_set.institution = self.institution
        first_submission_set.status = (
            submissions_models.RATED_SUBMISSION_STATUS)
        first_submission_set.save()

        # doc_field_sub for 2nd doc field:
        self.second_documentation_field_submission = (
            DocumentationFieldSubmissionFactory(
                documentation_field=self.second_documentation_field,
                value="Walnut Eyes"))

        # second submission set is migrated from first:
        second_submission_set = (
            self.second_documentation_field_submission.get_submissionset())
        second_submission_set.institution = self.institution
        second_submission_set.migrated_from = first_submission_set
        second_submission_set.save()

        # doc_field_sub for 3rd doc field:
        self.third_documentation_field_submission = (
            DocumentationFieldSubmissionFactory(
                documentation_field=self.third_documentation_field,
                value="Dick Van Dyke"))

        # third submission set is rated:
        third_submission_set = (
            self.third_documentation_field_submission.get_submissionset())
        third_submission_set.institution = self.institution
        third_submission_set.status = (
            submissions_models.RATED_SUBMISSION_STATUS)
        third_submission_set.save()

    def test_no_history(self):
        """With no history, is a dict with empty values returned?"""
        history = get_doc_field_submission_history_for_credit(
            credit=self.third_credit,
            institution=self.institution)
        self.assertDictEqual(history,
                             {self.third_documentation_field: set()})

    def test_some_history(self):
        """With some history, is it returned?"""
        self.setUpHistory()

        history = get_doc_field_submission_history_for_credit(
            credit=self.third_credit,
            institution=self.institution)
        
        expected_history = {
            self.third_documentation_field:
            set([self.second_documentation_field_submission,
                 self.first_documentation_field_submission])}

        self.assertDictEqual(history, expected_history)











        
        
