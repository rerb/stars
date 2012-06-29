from tastypie.api import Api
from stars.apps.credits.api import resources

v1_api = Api(api_name='v1')
for model in (resources.CategoryResource,
              resources.CreditResource,
              resources.CreditSetResource,
              resources.DocumentationFieldResource,
              resources.SubcategoryResource):
    v1_api.register(model())

urlpatterns = v1_api.urls
