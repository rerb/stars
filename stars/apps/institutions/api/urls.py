from tastypie.api import Api
from stars.apps.institutions.api import resources

v1_api = Api(api_name='v1')
v1_api.register(resources.InstitutionResource())

urlpatterns = v1_api.urls
