from tastypie.api import Api
from stars.apps.submissions.newapi import resources

v1_api = Api(api_name='v1')

for model in (resources.SubmissionSetResource,
              resources.CategorySubmissionResource,
              resources.SubcategorySubmissionResource,
              resources.CreditSubmissionResource,
              ):
    v1_api.register(model())

urlpatterns = v1_api.urls
