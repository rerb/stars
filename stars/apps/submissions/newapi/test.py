"""
Tests for submissions API.

These test cases fail if run via 'manage.py test' because the test
database has no data in it, and no fixtures are defined here.  They'll
run from the REPL as doctests, if you do this:

    import stars.apps.submissions.newapi.test as t
    import doctest
    doctest.testmod(t)
"""
import random

from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.newapi.resources import SubmissionSetResource
from stars.apps.api.test import StarsApiTestCase, get_random_visible_resource, \
     get_random_queryset_obj, new_test_result, setup_test_environment, \
     EmptyQuerysetError

def submissions_detail_path(submissionset=None):
    submissionset = submissionset or get_random_visible_resource(
        SubmissionSetResource)
    path = '/api/v1/submissions/{0}/'.format(submissionset.id)
    return path


class SubmissionResourceTestCase(StarsApiTestCase):

    list_path = '/api/v1/submissions/'

    def test_get_submissions_list_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubmissionResourceTestCase(\
                'test_get_submissions_list_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.list_path)

    def test_get_submissions_list(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubmissionResourceTestCase('test_get_submissions_list')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_submissions_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubmissionResourceTestCase(\
                'test_get_submissions_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(submissions_detail_path())

    def test_get_submissions_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubmissionResourceTestCase('test_get_submissions_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        path = submissions_detail_path()
        resp = self.get(path)
        self.assertValidJSONResponse(resp)


class CategorySubmissionResourceTestCase(StarsApiTestCase):

    list_path = submissions_detail_path() + 'category/'

    @property
    def detail_path(self):
        submissionset_resource = get_random_visible_resource(
            SubmissionSetResource)
        submissionset = SubmissionSet.objects.get(pk=submissionset_resource.id)
        category_submission = None
        while category_submission is None:
            try:
                category_submission = get_random_queryset_obj(
                    submissionset.categorysubmission_set)
            except EmptyQuerysetError:
                continue
        return (submissions_detail_path(submissionset) +
                'category/{0}/'.format(category_submission.category_id))

    def test_get_categorysubmission_list_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_list_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.list_path)

    def test_get_categorysubmission_list(self):
        """
        >>> test_result = new_test_result()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_list')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_categorysubmission_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.detail_path)

    def test_get_categorysubmission_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)


class SubcategorySubmissionResourceTestCase(StarsApiTestCase):

    list_path = submissions_detail_path() + 'subcategory/'

    @property
    def detail_path(self):
        subcategory_submission = None
        while subcategory_submission is None:
            submissionset_resource = get_random_visible_resource(
                SubmissionSetResource)
            submissionset = SubmissionSet.objects.get(
                pk=submissionset_resource.id)
            try:
                category_submission = get_random_queryset_obj(
                    submissionset.categorysubmission_set)
                subcategory_submission = get_random_queryset_obj(
                    category_submission.subcategorysubmission_set)
            except EmptyQuerysetError:
                continue
        return (submissions_detail_path(submissionset) +
                'subcategory/{0}/'.format(
                    subcategory_submission.subcategory_id))

    def test_get_subcategorysubmission_list_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_list_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.list_path)

    def test_get_subcategorysubmission_list(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_list')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_subcategorysubmission_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.detail_path)

    def test_get_subcategorysubmission_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)


class CreditSubmissionResourceTestCase(StarsApiTestCase):

    list_path = submissions_detail_path() + 'credit/'

    @property
    def detail_path(self):
        credit_submission = None
        while credit_submission is None:
            submissionset_resource = get_random_visible_resource(
                SubmissionSetResource)
            submissionset = SubmissionSet.objects.get(
                pk=submissionset_resource.id)
            try:
                category_submission = get_random_queryset_obj(
                    submissionset.categorysubmission_set)
                subcategory_submission = get_random_queryset_obj(
                    category_submission.subcategorysubmission_set)
                credit_submission = get_random_queryset_obj(
                    subcategory_submission.creditusersubmission_set)
            except EmptyQuerysetError:
                continue
        return (submissions_detail_path(submissionset) +
                'credit/{0}/'.format(
                    credit_submission.credit_id))

    def test_get_creditsubmission_list_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_list_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.list_path)

    def test_get_creditsubmission_list(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_list')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_creditsubmission_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.detail_path)

    def test_get_creditsubmission_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)


class DocumentationFieldSubmissionResourceTestCase(StarsApiTestCase):

    @property
    def detail_path(self):
        field_submission = None
        while field_submission is None:
            submissionset_resource = get_random_visible_resource(
                SubmissionSetResource)
            submissionset = SubmissionSet.objects.get(
                pk=submissionset_resource.id)
            try:
                category_submission = get_random_queryset_obj(
                    submissionset.categorysubmission_set)
                subcategory_submission = get_random_queryset_obj(
                    category_submission.subcategorysubmission_set)
                credit_submission = get_random_queryset_obj(
                    subcategory_submission.creditusersubmission_set)
            except EmptyQuerysetError:
                continue
            field_submissions = credit_submission.get_submission_fields()
            if len(field_submissions) == 0:
                continue
            random_index = random.randint(0, len(field_submissions) - 1)
            field_submission = field_submissions[random_index]
        return (submissions_detail_path(submissionset) +
                'field/{0}/'.format(field_submission.documentation_field_id))

    def test_get_documentationfieldsubmission_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = DocumentationFieldSubmissionResourceTestCase(\
                'test_get_documentationfieldsubmission_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.detail_path)

    def test_get_documentationfieldsubmission_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = DocumentationFieldSubmissionResourceTestCase(\
                    'test_get_documentationfieldsubmission_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)
