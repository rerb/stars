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

from django.contrib.auth.models import User
from tastypie.models import ApiKey
from tastypie.test import ResourceTestCase

from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.newapi.resources import SubmissionSetResource

def get_random_resource(resource):
    return get_random_queryset_obj(resource._meta.queryset)

def get_random_queryset_obj(queryset):
    random_index = random.randint(0, queryset.count() - 1)
    return [ instance for instance in queryset.all() ][random_index]

def new_test_result():
    """Get a unittest.TestResult object.  Used in doctests."""
    setup_test_environment()
    from unittest import TestResult
    return TestResult()

def setup_test_environment():
    """Set up the test environment."""
    from django.test.utils import setup_test_environment
    setup_test_environment()


class StarsApiTestCase(ResourceTestCase):

    def setUp(self):
        super(StarsApiTestCase, self).setUp()

        # Create a user:
        self.user, self.created_user = User.objects.get_or_create(
            username='johndoe')

        # Create an API key for the user:
        _, self.created_api_key = ApiKey.objects.get_or_create(user=self.user)

        # Use url_params until HTTP auth header is working - then
        # switch to get_credentials().
        self.credentials_as_url_params = {'username': self.user.username,
                                          'api_key': self.user.api_key.key}

    def tearDown(self):
        if self.created_api_key:
            ApiKey.objects.get(user=self.user).delete()
        if self.created_user:
            User.objects.get(pk=self.user.id).delete()

    def get(self, path):
        """Do a GET using the default credentials."""
        return self.api_client.get(path, data=self.credentials_as_url_params)

    def requires_auth(self, path):
        # Make sure authentication is on for path.
        resp = self.api_client.get(path)
        self.assertHttpUnauthorized(resp)

    # get_credentials() is pretty useless since self.create_apikey()
    # returns an HTTP auth header, and authentication via HTTP auth
    # header doesn't seem to be working.  When it does, use get_credentials(),
    # rather than self.credentials_as_params in self.get() below.
    # def get_credentials(self):
    #     return self.create_apikey(username=self.user.username,
    #                               api_key=self.user.api_key.key)

    # def test_create_apikey(self):
    #     # Try api key authentication using ResourceTestCase.create_apikey().
    #     credentials = self.create_apikey(username=self.user.username,
    #                                      api_key=self.user.api_key.key)
    #     resp = self.api_client.get('/api/v1/submissions/',
    #                                authentication=credentials)
    #     self.assertHttpOK(resp)


def submissions_detail_path(submissionset=None):
    submissionset = submissionset or get_random_resource(SubmissionSetResource)
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
        submissionset_resource = get_random_resource(SubmissionSetResource)
        submissionset = SubmissionSet.objects.get(pk=submissionset_resource.id)
        category_submission = get_random_queryset_obj(
            submissionset.categorysubmission_set)
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
        submissionset_resource = get_random_resource(SubmissionSetResource)
        submissionset = SubmissionSet.objects.get(pk=submissionset_resource.id)
        category_submission = get_random_queryset_obj(
            submissionset.categorysubmission_set)
        subcategory_submission = get_random_queryset_obj(
            category_submission.subcategorysubmission_set)
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
