"""Tests for apps.tool.my_submission.credit_history_tab."""
from django.test import TestCase

from stars.apps.submissions.models import (RATED_SUBMISSION_STATUS,
                                           SubmissionSet)
from stars.test_factories import *

from ..credit_history import *


class GetSubmissionsetsToIncludeInHistoryTest(TestCase):
    
    def setUp(self):
        SubmissionSet.objects.all().delete()
        self.institution = InstitutionFactory()

    def test_rated_are_included(self):
        """Are rated SubmissionSets included?"""
        ss = SubmissionSetFactory(
            status=RATED_SUBMISSION_STATUS,
            institution=self.institution)
        self.assertEqual(
            get_submissionsets_to_include_in_history(self.institution),
            [ss])

    def test_unrated_and_not_migrated_to_are_excluded(self):
        """Are unrated and not migrated_to SubmissionSets excluded?"""
        ss = SubmissionSetFactory(institution=self.institution)
        self.assertEqual(
            get_submissionsets_to_include_in_history(self.institution),
            [])

    def test_migrated_to_are_included(self):
        """Are migrated_to SubmissionSets included?"""
        ss1 = SubmissionSetFactory(institution=self.institution)
        ss = SubmissionSetFactory(migrated_to=ss1,
                                  institution=self.institution)
        self.assertEqual(
            get_submissionsets_to_include_in_history(self.institution),
            [ss])


class GetPreviousDocFieldVersionsTest(TestCase):

    def test_it_works(self):
        """Uh, does it work?"""
        first_doc_field = DocumentationFieldFactory()
        second_doc_field = DocumentationFieldFactory(
            previous_version=first_doc_field)
        third_doc_field = DocumentationFieldFactory(
            previous_version=second_doc_field)
        self.assertDictEqual(
            get_previous_doc_field_versions(third_doc_field),
            {first_doc_field.get_creditset(): first_doc_field,
             second_doc_field.get_creditset(): second_doc_field})













        
        
