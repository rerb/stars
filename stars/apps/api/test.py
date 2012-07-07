from exceptions import IndexError
import random

from django.contrib.auth.models import User
from django.utils import simplejson
from tastypie.models import ApiKey
from tastypie.test import ResourceTestCase

API_URI = 'http://localhost:8000/api/0.1'

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
    try:
        return list(queryset.all())[random_index]
    except IndexError:
        # As far as I can see, an IndexError should never happen here.
        # Still, it does.  So screw it, and return the first obj:
        return list(queryset.all())[0]


class EmptyQuerysetError(Exception):

    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return repr(self.message)


class StarsApiTestCase(ResourceTestCase):

    fixtures = ['api_test_fixture.json']

    def setUp(self):
        super(StarsApiTestCase, self).setUp()

        # Create a user:
        self.user, self.created_user = User.objects.get_or_create(
            username='johndoe')

        # Create an API key for the user:
        _, self.created_api_key = ApiKey.objects.get_or_create(user=self.user)

    def tearDown(self):
        if self.created_api_key:
            ApiKey.objects.get(user=self.user).delete()
        if self.created_user:
            User.objects.get(pk=self.user.id).delete()

    def get(self, path):
        """Do a GET using the default credentials."""
        return self.api_client.get(path,
                                   authentication=self.get_credentials())

    def requires_auth(self, path):
        """Does path require auth?"""
        resp = self.api_client.get(path)
        self.assertHttpUnauthorized(resp)

    def assertValidJSONResponseNotError(self, response):
        """Response is valid JSON and not an error message."""
        self.assertValidJSONResponse(response)
        content_dict = simplejson.loads(response.content)
        self.assertNotIn('error_message', content_dict)

    def get_credentials(self):
        return self.create_apikey(username=self.user.username,
                                  api_key=self.user.api_key.key)
