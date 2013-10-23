"""Tests for apps.submissions.models.DocumentationFieldSubmission.
"""
from unittest import TestCase

import testfixtures

from stars.apps.migrations.utils import (migrate_creditset,
                                         migrate_ss_version)
from stars.apps.submissions.models import DocumentationFieldSubmission
from stars.test_factories import (CreditSetFactory,
                                  DocumentationFieldFactory,
                                  DocumentationFieldSubmissionFactory)


class DocumentationFieldSubmissionTest(TestCase):

    def test_get_migrated_value(self):
        """Does get_migrated_value work?
        
        Huge dependencies on migrate_creditset and migrate_ss_version.
        """
        ORIGINAL_VALUE = 'original value'
        
        documentation_field = DocumentationFieldFactory()
        documentation_field_submission = DocumentationFieldSubmissionFactory(
            documentation_field=documentation_field,
            value=ORIGINAL_VALUE)

        original_creditset = documentation_field.get_creditset()
        original_submissionset = (
            documentation_field_submission.get_submissionset())

        original_submissionset.creditset = original_creditset
        original_submissionset.save()

        new_creditset = migrate_creditset(old_cs=original_creditset,
                                          new_version_name='9999',
                                          release_date='2000-01-01')
        
        new_submissionset = migrate_ss_version(old_ss=original_submissionset,
                                               new_cs=new_creditset)

        documentation_field_submission.value = 'new value'
        documentation_field_submission.save()

        self.assertEqual(documentation_field_submission.get_migrated_value(),
                         ORIGINAL_VALUE)


    # def setUp(self):
    #     super(VersionMigrationTest, self).setUp()
    #     self.first_creditset, self.second_creditset = make_two_creditsets()
    #     self._submissionset = None

    # @property
    # def submissionset(self):
    #     if not self._submissionset:
    #         self._submissionset = SubmissionSetFactory(
    #             creditset=self.first_creditset)
    #     return self._submissionset

    # def test_migrate_submission_sets_migrated_from(self):
    #     """Does migrate_submission() set SubmissionSet.migrated_from?"""

    #     new_submissionset = SubmissionSetFactory(
    #         institution=self.submissionset.institution,
    #         creditset=self.second_creditset)

    #     _ = utils.migrate_submission(old_ss=self.submissionset,
    #                                  new_ss=new_submissionset)
    #     import ipdb; ipdb.set_trace()
    #     self.assertEqual(new_submissionset.migrated_from,
    #                      self.submissionset)



        
        
        
