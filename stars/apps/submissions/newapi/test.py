"""
Tests for submissions API.

There's a problem (with the test fixtures, I suppose) that keeps these
tests from passing via 'manage.py test'.  They'll pass when run from a
'manage.py shell' REPL (running against your dev database -- assuming
you have the data they're looking for) when run via doctest, like this:

   #>>> import doctest
   #>>> from stars.apps.submissions.newapi import test
   #>>> doctest.testmod(test)
"""
import json

from stars.apps.api.test import StarsApiTestCase
from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.newapi.resources import SubmissionSetResource

submissions_list_path = '/api/0.1/submissions/'

def submissions_detail_path(submissionset_id=34):
    return '{list_path}{submissionset_id}/'.format(
        list_path=submissions_list_path,
        submissionset_id=submissionset_id)

def submissionset_for_subcategorysubmission(subcategorysubmission):
    categorysubmission = subcategorysubmission.category_submission
    return categorysubmission.submissionset

def subcatsub_with_points(from_reporter=True):
    """Get a SubcategorySubmission with points, related to a
    visible SubmissionSet, optionally submitted by a reporter.
    """
    for submission_from_reporter in \
        SubmissionSetResource._meta.queryset.filter(
            reporter_status=from_reporter):
      for catsub in submission_from_reporter.categorysubmission_set.all():
            for subcatsub in catsub.subcategorysubmission_set.filter(
                    points__gt=0):
                return subcatsub


class SubmissionSetResourceTestCase(StarsApiTestCase):

    def test_get_submissions_list_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubmissionSetResourceTestCase(\
                    'test_get_submissions_list_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(submissions_list_path)

    def test_get_submissions_list(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubmissionSetResourceTestCase(\
                    'test_get_submissions_list')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(submissions_list_path)
        self.assertValidJSONResponse(resp)

    def test_get_submissions_detail_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubmissionSetResourceTestCase(\
                    'test_get_submissions_detail_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(submissions_detail_path())

    def test_get_submissions_detail(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubmissionSetResourceTestCase(\
                    'test_get_submissions_detail')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(submissions_detail_path())
        self.assertValidJSONResponse(resp)

    def test_get_hidden_submission(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubmissionSetResourceTestCase('test_get_hidden_submission')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        # Get a submission set that should be filtered:
        for submissionset in SubmissionSet.objects.all():
            if submissionset not in SubmissionSetResource._meta.queryset:
                hidden_submissionset = submissionset
                break
        resp = self.get(submissions_detail_path(hidden_submissionset.id))
        self.assertHttpNotFound(resp)

    def test_unrated_submissions_are_hidden(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubmissionSetResourceTestCase(\
                    'test_unrated_submissions_are_hidden')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(submissions_list_path + '?limit=0')
        payload = json.loads(resp.content)
        visible_submissionsets = payload['objects']
        visible_submissionset_ids = [
            submissionset['resource_uri'].split('/')[-2] for submissionset
            in visible_submissionsets ]
        rated_submissionset_ids = [ str(submissionset.id) for submissionset in
                                    SubmissionSet.objects.get_rated() ]
        self.assertTrue(
            set(visible_submissionset_ids) == set(rated_submissionset_ids))


class CategorySubmissionResourceTestCase(StarsApiTestCase):

    list_path = submissions_detail_path(34) + 'category/'
    detail_path = list_path + '1/'

    def test_get_categorysubmission_list_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_list_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.list_path)

    def test_get_categorysubmission_list(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_list')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_categorysubmission_detail_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_detail_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.detail_path)

    def test_get_categorysubmission_detail(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_detail')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)


class SubcategorySubmissionResourceTestCase(StarsApiTestCase):

    def list_path(self, submissionset_id=75):
        return submissions_detail_path(submissionset_id) + 'subcategory/'

    def detail_path(self, submissionset_id=75, subcategory_id=3):
        return '{list_path}{subcategory_id}/'.format(
            list_path=self.list_path(submissionset_id),
            subcategory_id=subcategory_id)

    def test_get_subcategorysubmission_list_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_list_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.list_path())

    def test_get_subcategorysubmission_list(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_list')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.list_path())
        self.assertValidJSONResponse(resp)

    def test_get_subcategorysubmission_detail_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_detail_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.detail_path())

    def test_get_subcategorysubmission_detail(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_detail')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.detail_path())
        self.assertValidJSONResponse(resp)

    def test_dehydrate_points(self):
        """Points for SubmissionSets from data reports should be
        hidden.

        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_dehydrate_points')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        # Make sure points aren't None for everybody:
        subcatsub_with_points_not_from_reporter = subcatsub_with_points(
            from_reporter=False)
        subcategory_id = subcatsub_with_points_not_from_reporter.subcategory.id
        resp = self.get(self.detail_path(
            submissionset_id=submissionset_for_subcategorysubmission(
                subcatsub_with_points_not_from_reporter).id,
            subcategory_id=subcategory_id))
        self.assertValidJSONResponse(resp)
        payload = json.loads(resp.content)
        self.assertTrue(payload['points'] is not None)
        # Now check that they're None for reporters:
        subcatsub_with_points_from_reporter = subcatsub_with_points(
            from_reporter=True)
        subcategory_id = subcatsub_with_points_from_reporter.subcategory.id
        resp = self.get(self.detail_path(
            submissionset_id=submissionset_for_subcategorysubmission(
                subcatsub_with_points_from_reporter).id,
            subcategory_id=subcategory_id))
        self.assertValidJSONResponse(resp)
        payload = json.loads(resp.content)
        self.assertTrue(payload['points'] is None)


class CreditSubmissionResourceTestCase(StarsApiTestCase):

    list_path = submissions_detail_path(75) + 'credit/'
    detail_path = list_path + '17/'

    def test_get_creditsubmission_list_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_list_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.list_path)

    def test_get_creditsubmission_list(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_list')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_creditsubmission_detail_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_detail_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.detail_path)

    def test_get_creditsubmission_detail(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_detail')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)


class DocumentationFieldSubmissionResourceTestCase(StarsApiTestCase):

    detail_path = submissions_detail_path(75) + 'field/167/'

    def test_get_documentationfieldsubmission_detail_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = DocumentationFieldSubmissionResourceTestCase(\
                'test_get_documentationfieldsubmission_detail_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.detail_path)

    def test_get_documentationfieldsubmission_detail(self):
        """
        >>> from unittest import TestResult
        >>> result = TestResult()
        >>> test = DocumentationFieldSubmissionResourceTestCase(\
                    'test_get_documentationfieldsubmission_detail')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)
