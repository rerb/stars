"""
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

API_URI = 'http://localhost:8000/api/v1'

def get_random_visible_resource(resource):
    """Get a random instance of an ApiResource that's exposed.

    Any filtering done in the resource's _meta.queryset is respected here.
    """
    return get_random_queryset_obj(resource._meta.queryset)

def get_random_queryset_obj(queryset):
    """Get a random object from a queryset."""
    if queryset.count() == 0:
        raise EmptyQuerysetError
    random_index = random.randint(0, queryset.count() - 1)
    return [ instance for instance in queryset.all() ][random_index]

def new_test_result():
    """Get a unittest.TestResult object.  Used in doctests below."""
    setup_test_environment()
    from unittest import TestResult
    return TestResult()

def setup_test_environment():
    """Set up the test environment.  Used in doctests below."""
    from django.test.utils import setup_test_environment
    setup_test_environment()


class EmptyQuerysetError(Exception):
    pass


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
