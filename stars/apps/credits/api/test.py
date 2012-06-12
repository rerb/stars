"""Hey, wtf is up with this test?  Runs ok from within a shell started
via manage.py, but not via 'manage.py test'.  Will fix that up later.  For
now, just ...

    $ manage.py shell
    >>> import stars.apps.credits.api.test.py as test
    >>> tester = test.CreditsApiTest()
    >>> tester.runTest()

... and don't forget to patch runTest() to include any new tests you
add below.
"""
import random
import uuid

from django.contrib.auth.models import User
import slumber
from tastypie.models import ApiKey
from tastypie.test import ResourceTestCase

import stars.apps.credits.models as credits_models


API_BASE_URL = 'http://localhost:8000/api/v1'


class CreditsApiTest(ResourceTestCase):

    def __init__(self):
        super(CreditsApiTest, self).__init__()
        self.registered_user_password = 'password'

    def setUp(self):
        super(CreditsApiTest, self).setUp()
        self.registered_user = self.new_user(register=True)
        self.unregistered_user = self.new_user(register=False)
        self.registered_api = self.api(self.registered_user)

    def tearDown(self):
        for key in (self.registered_user.pk, self.unregistered_user.pk):
            User.objects.get(pk=key).delete()  # cascades into ApiKey delete?
        super(CreditsApiTest, self).tearDown()

    def api(self, user=None):
        if user:
            return slumber.API(
                API_BASE_URL,
                default_params={'username': user.username,
                                'api_key': user.api_key.key,
                                'password': self.registered_user_password})
        else:
            return slumber.API(API_BASE_URL)

    def new_user(self, register=True):
        username = str(uuid.uuid1())[:11]
        email = '{username}@example.com'.format(username=username)
        password = self.registered_user_password
        user = User.objects.create_user(username=username, email=email,
                                        password=password)
        if register:
            key = ApiKey.objects.create(user=user)
            key.save()
        return user

    def runTest(self):
        self.setUp()
        self.test_anonymous()
        self.test_url_params_authenticated()
        self.test_default_params_authenticated()
        model_to_resource_name_map = {
            credits_models.CreditSet: None,
            credits_models.Category: None,
            credits_models.Subcategory: None,
            credits_models.Credit: None,
            credits_models.DocumentationField: 'field' }
        for model, resource_name in model_to_resource_name_map.items():
            self.test_url_credits_model(model=model,
                                        resource_name=resource_name)
            self.test_url_credits_model_id(model=model,
                                           resource_name=resource_name)
#        self.test_headers_authenticated()
        self.tearDown()

    def test_anonymous(self):
        if not getattr(self, 'api_client', None):
            self.setUp()  # what about tearing down?
            teardown = True
        response = self.api_client.get(API_BASE_URL + '/credits/creditset/')
        try:
            self.assertHttpUnauthorized(response)
        finally:
            try:
                if teardown:
                    self.tearDown()
            except NameError:
                pass

    def test_api_key_no_password(self):
        raise Exception

    def test_default_params_authenticated(self):
        user = self.registered_user
        api = self.api(user)
        return api.credits.creditset.get()

    def test_url_params_authenticated(self):
        user = self.registered_user
        api = self.api()
        return api.credits.creditset.get(username=user.username,
                                         api_key=user.api_key.key)

    def test_url_credits_model(self, model, resource_name=None):
        """Test that .../credits/<model> returns all model instances."""
        resource_name = resource_name or model._meta.object_name.lower()
        json_response = eval(
            'self.registered_api.credits.{0}.get()'.format(resource_name))
        assert(json_response['meta']['total_count'] ==
               model.objects.count())

    def test_url_credits_model_id(self, model, resource_name=None):
        """Test that .../credits/<model>/<id> returns the correct
        model instance."""
        model_ids = [ instance.id for instance in model.objects.all() ]
        lookup_id = model_ids[random.randint(0, len(model_ids) - 1)]
        resource_name = resource_name or model._meta.object_name.lower()
        json_response = eval(
            'self.registered_api.credits.{0}({1}).get()'.format(resource_name,
                                                                lookup_id))
        model_instance = model.objects.get(pk=lookup_id)
        assert(int(json_response['id']) == model_instance.pk)


    # def test_headers_authenticated(self):
    #     user = self.registered_user
    #     headers = { 'Authorization':
    #                 'ApiKey {username}:{api_key}'.format(
    #                 username=user.username, api_key=user.api_key.key) }
    #     api = self.api()
    #     api.credits.credit.get(headers=headers)
