from tastypie.api import Api
from stars.apps.institutions.api import resources

api = Api(api_name='0.1')
api.register(resources.InstitutionResource())

urlpatterns = api.urls
