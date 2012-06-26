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

API_URI = 'http://localhost:8000/api/v1'


class ApiTest(ResourceTestCase):

    def __init__(self, app_name):
        """app_name (e.g., 'credits', 'submissions') is used to
        construct the API uris, e.g.,

               http://server/api/v1/<app_name>/resource/
           """
        super(ApiTest, self).__init__()
        self.registered_user_password = 'password'
        self.app_name = app_name

    def setUp(self):
        super(ApiTest, self).setUp()
        self.registered_user = self.new_user(register=True)
        self.unregistered_user = self.new_user(register=False)
        self.registered_api = self.api(self.registered_user)

    def tearDown(self):
        """Delete the users and api_keys we created in setUp()."""
        for key in (self.registered_user.pk, self.unregistered_user.pk):
            User.objects.get(pk=key).delete()  # cascades into ApiKey delete?
        super(ApiTest, self).tearDown()

    def api(self, user=None):
        """If specified, user is used for authentication."""
        if user:
            session = slumber.requests.session(
                params={'username': user.username,
                        'api_key': user.api_key.key})
            return slumber.API(API_URI, session=session)
        else:
            return slumber.API(API_URI)

    def new_user(self, register=True):
        """Make a new user. If register is True, get him an api key."""
        username = str(uuid.uuid1())[:11]
        email = '{username}@example.com'.format(username=username)
        password = self.registered_user_password
        user = User.objects.create_user(username=username, email=email,
                                        password=password)
        if register:
            key = ApiKey.objects.create(user=user)
            key.save()
        return user

    def runTest(self, models_map=None, tearDown=True):
        """Runs tests for this api app (self.app_name).

        models_map is a dictionary specifying which models to run
        test_url_credits() and test_url_credits_model_id() for.  Keys
        are the models, and values are the resource name (or None, if
        the resource name is the model name lower()'ed).
        """
        self.setUp()
        self.test_anonymous()
        self.test_session_authenticated()
        self.test_get_args_authenticated()
        if models_map:
            for model, resource_name in models_map.items():
                self.test_url_credits_model(model=model,
                                            resource_name=resource_name)
                self.test_url_credits_model_id(model=model,
                                               resource_name=resource_name)
        # self.test_headers_authenticated()
        if tearDown:
            self.tearDown()

    def test_anonymous(self, resource_name=None):
        """Is an anonymous request rejected?"""
        resource_name = resource_name or self.default_resource_name
        if not getattr(self, 'api_client', None):
            self.setUp()  # what about tearing down?
            teardown = True
        response = self.api_client.get('/'.join([API_URI,
                                                 self.app_name,
                                                 resource_name,
                                                 '']))
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

    def test_session_authenticated(self, resource_name=None):
        """Does passing session arg to slumber.API
        work?  Not really our concern, but . . ."""
        resource_name = resource_name or self.default_resource_name
        user = self.registered_user
        api = self.api(user)
        return eval('api.{0}.{1}.get()'.format(self.app_name, resource_name))

    def test_get_args_authenticated(self, resource_name=None):
        """Does passing username and api key as args to get() work?"""
        resource_name = resource_name or self.default_resource_name
        user = self.registered_user
        api = self.api()
        source = """api.{0}.{1}.get(username=user.username,
                                    api_key=user.api_key.key)""".format(
                                        self.app_name, resource_name)
        return eval(source)

    def test_url_credits_model(self, model, resource_name=None,
                               objects=None):
        """Does {self.app_name}/<model> returnsall model instances?"""
        resource_name = resource_name or model._meta.object_name.lower()
        json_response = eval(
            'self.registered_api.{0}.{1}.get()'.format(self.app_name,
                                                       resource_name))
        objects = objects or model.objects
        assert(json_response['meta']['total_count'] ==
               objects.count())

    def test_url_credits_model_id(self, model, resource_name=None):
        """Does {self.app_name}/<model>/<id> return the correct
        model instance?"""
        model_ids = [ instance.id for instance in model.objects.all() ]
        lookup_id = model_ids[random.randint(0, len(model_ids) - 1)]
        resource_name = resource_name or model._meta.object_name.lower()
        json_response = eval(
            'self.registered_api.{0}.{1}({2}).get()'.format(self.app_name,
                                                            resource_name,
                                                            lookup_id))
        model_instance = model.objects.get(pk=lookup_id)
        assert(int(json_response['id']) == model_instance.pk)

    # def test_headers_authenticated(self):
    #     user = self.registered_user
    #     headers = { 'Authorization':
    #                 'ApiKey {username}:{api_key}'.format(
    #                 username=user.username, api_key=user.api_key.key) }
    #     api = self.api()
    #     api.credit.get(headers=headers)
