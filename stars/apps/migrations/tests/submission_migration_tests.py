"""
    Submission Migration unit tests
"""
from django.test import TestCase

from stars.apps.credits.models import (Category,
                                       Credit,
                                       Subcategory,
                                       DocumentationField)
from stars.apps.migrations import utils
from stars.apps.submissions.models import (CreditUserSubmission,
                                           NumericSubmission)
from stars.test_factories import (CreditSetFactory,
                                  SubmissionSetFactory)


def make_two_creditsets():
    return (CreditSetFactory(release_date='1970-01-01'),
            CreditSetFactory(release_date='1971-10-07'))


class VersionMigrationTest(TestCase):

    def setUp(self):
        super(VersionMigrationTest, self).setUp()
        self.first_creditset, self.second_creditset = make_two_creditsets()
        self._submissionset = None

    @property
    def submissionset(self):
        if not self._submissionset:
            self._submissionset = SubmissionSetFactory(
                creditset=self.first_creditset)
        return self._submissionset

    def test_migrate_submission_sets_migrated_from(self):
        """Does migrate_submission() set SubmissionSet.migrated_from?"""

        new_submissionset = SubmissionSetFactory(
            institution=self.submissionset.institution,
            creditset=self.second_creditset)

        utils.migrate_submission(old_submissionset=self.submissionset,
                                 new_submissionset=new_submissionset)

        self.assertEqual(new_submissionset.migrated_from,
                         self.submissionset)


class MigrateSubmissionTestCase(TestCase):

    def get_creditset(self):
        creditset = CreditSetFactory()

        self.innovations_category = Category.objects.create(
            creditset=creditset,
            abbreviation="IN")
        self.innovations_subcategory = Subcategory.objects.create(
            category=self.innovations_category,
            title="Innovation")
        self.innovations_credit = Credit.objects.create(
            subcategory=self.innovations_subcategory,
            identifier="INNOVATION",
            point_value=10)
        self.innovations_documentation_field = (
            DocumentationField.objects.create(
                credit=self.innovations_credit,
                type="numeric"))

        self.not_innovations_subcategory = Subcategory.objects.create(
            category=self.innovations_category,
            title="Not Innovation")
        self.not_innovations_credit = Credit.objects.create(
            subcategory=self.not_innovations_subcategory,
            identifier="NOT-INNOVATION",
            point_value=20)
        self.not_innovations_documentation_field = (
            DocumentationField.objects.create(
                credit=self.not_innovations_credit,
                type="numeric"))

        return creditset

    def get_submissionset(self, creditset):
        submissionset = SubmissionSetFactory(creditset=creditset)

        self.innovations_numeric_submission = NumericSubmission.objects.create(
            documentation_field=self.innovations_documentation_field,
            credit_submission=CreditUserSubmission.objects.get(
                subcategory_submission__subcategory__slug='innovation'),
            value=10)

        self.not_innovations_numeric_submission = (
            NumericSubmission.objects.create(
                documentation_field=self.not_innovations_documentation_field,
                credit_submission=CreditUserSubmission.objects.get(
                    subcategory_submission__subcategory__slug='not-innovation'),
                value=20))

        return submissionset

    def test_innovations_credits_dont_migrate_for_rated_submission(self):
        """Do Innovation credits migrate from rated submissions?
        They shouldn't.
        """
        creditset = self.get_creditset()

        submissionset = self.get_submissionset(creditset=creditset)
        submissionset.status = "r"
        submissionset.save()

        new_submissionset = utils.new_submissionset_for_old_submissionset(
            old_submissionset=submissionset,
            new_creditset=submissionset.creditset)

        new_submissionset = utils.migrate_submission(
            old_submissionset=submissionset,
            new_submissionset=new_submissionset)

        new_credit_submissions = new_submissionset.get_credit_submissions()

        new_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'innovation'][0]
        self.assertEqual(
            0, new_innovations_credit_submission.numericsubmission_set.count())

        new_not_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'not-innovation'][0]
        self.assertEqual(
            1, new_not_innovations_credit_submission.numericsubmission_set.count())
        new_not_innovations_numericsubmission = (
            new_not_innovations_credit_submission.numericsubmission_set.all()[0])
        self.assertEqual(20, new_not_innovations_numericsubmission.value)

    def test_innovations_credits_migrate_if_specified(self):
        """Do Innovation credits migrate from rated submissions if told to?
        """
        creditset = self.get_creditset()

        submissionset = self.get_submissionset(creditset=creditset)
        submissionset.status = "r"
        submissionset.save()

        new_submissionset = utils.new_submissionset_for_old_submissionset(
            old_submissionset=submissionset,
            new_creditset=submissionset.creditset)

        new_submissionset = utils.migrate_submission(
            old_submissionset=submissionset,
            new_submissionset=new_submissionset,
            keep_innovation=True)

        new_credit_submissions = new_submissionset.get_credit_submissions()

        new_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'innovation'][0]
        self.assertEqual(
            1, new_innovations_credit_submission.numericsubmission_set.count())
        new_innovations_numericsubmission = (
            new_innovations_credit_submission.numericsubmission_set.all()[0])
        self.assertEqual(10, new_innovations_numericsubmission.value)

        new_not_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'not-innovation'][0]
        self.assertEqual(
            1, new_not_innovations_credit_submission.numericsubmission_set.count())
        new_not_innovations_numericsubmission = (
            new_not_innovations_credit_submission.numericsubmission_set.all()[0])
        self.assertEqual(20, new_not_innovations_numericsubmission.value)

    def test_innovations_credits_migrate_if_submission_is_unrated(self):
        """Do Innovation credits migrate from unrated submissions?
        """
        creditset = self.get_creditset()

        submissionset = self.get_submissionset(creditset=creditset)
        submissionset.save()

        new_submissionset = utils.new_submissionset_for_old_submissionset(
            old_submissionset=submissionset,
            new_creditset=submissionset.creditset)

        new_submissionset = utils.migrate_submission(
            old_submissionset=submissionset,
            new_submissionset=new_submissionset)

        new_credit_submissions = new_submissionset.get_credit_submissions()

        new_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'innovation'][0]
        self.assertEqual(
            1, new_innovations_credit_submission.numericsubmission_set.count())
        new_innovations_numericsubmission = (
            new_innovations_credit_submission.numericsubmission_set.all()[0])
        self.assertEqual(10, new_innovations_numericsubmission.value)

        new_not_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'not-innovation'][0]
        self.assertEqual(
            1, new_not_innovations_credit_submission.numericsubmission_set.count())
        new_not_innovations_numericsubmission = (
            new_not_innovations_credit_submission.numericsubmission_set.all()[0])
        self.assertEqual(20, new_not_innovations_numericsubmission.value)
