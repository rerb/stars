from tastypie.api import Api
from stars.apps.credits.api import resources

api = Api(api_name='0.1')
for model in (resources.CategoryResource,
              resources.CreditResource,
              resources.CreditSetResource,
              resources.DocumentationFieldResource,
              resources.SubcategoryResource):
    api.register(model())

urlpatterns = api.urls
