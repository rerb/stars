from tastypie.api import Api
from stars.apps.credits.api import resources

v1_api = Api(api_name='v1')
v1_api.register(resources.CategoryResource())
v1_api.register(resources.CreditResource())
v1_api.register(resources.CreditSetResource())
v1_api.register(resources.DocumentationFieldResource())
v1_api.register(resources.SubcategoryResource())

urlpatterns = v1_api.urls
