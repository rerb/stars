from tastypie.api import Api
from stars.apps.submissions.newapi import resources

v1_api = Api(api_name='v1')

for model in (resources.SubmissionSetResource,
              resources.CategorySubmissionResource,
              resources.SubcategorySubmissionResource,
              resources.CreditSubmissionResource,
              # resources.DocumentationFieldResource,
              ):
    v1_api.register(model())

# v1_api.register(resources.CategoryResource())
# v1_api.register(resources.CreditResource())
# v1_api.register(resources.CreditSetResource())
# v1_api.register(resources.DocumentationFieldResource())
# v1_api.register(resources.SubcategoryResource())
urlpatterns = v1_api.urls
