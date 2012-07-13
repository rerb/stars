from django.contrib.auth.models import User
from django.utils import simplejson
from tastypie.models import ApiKey
from tastypie.test import ResourceTestCase

API_URI = 'http://localhost:8000/api/0.1'


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

    # HTTP method wrappers:

    def delete(self, path):
        """Do a DELETE using the default credentials."""
        return self.api_client.delete(path,
                                      authentication=self.get_credentials())

    def get(self, path):
        """Do a GET using the default credentials."""
        return self.api_client.get(path,
                                   authentication=self.get_credentials())

    def patch(self, path, data=None):
        """Do a PATCH using the default credentials."""
        data = data or {}
        return self.api_client.patch(path,
                                     authentication=self.get_credentials(),
                                     data=data)

    def post(self, path, data=None):
        """Do a POST using the default credentials."""
        data = data or {}
        return self.api_client.post(path,
                                    authentication=self.get_credentials(),
                                    data=data)

    def put(self, path, data=None):
        """Do a PUT using the default credentials."""
        data = data or {}
        return self.api_client.put(path,
                                   authentication=self.get_credentials(),
                                   data=data)

    # Misc.

    def assertValidJSONResponseNotError(self, response):
        """Response is valid JSON and not an error message."""
        self.assertValidJSONResponse(response)
        content_dict = simplejson.loads(response.content)
        self.assertNotIn('error_message', content_dict)

    def get_credentials(self):
        return self.create_apikey(username=self.user.username,
                                  api_key=self.user.api_key.key)

    def requires_auth(self, path):
        """Does path require authentication?"""
        resp = self.api_client.get(path)
        self.assertHttpUnauthorized(resp)
