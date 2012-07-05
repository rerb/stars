from tastypie.api import Api
from stars.apps.submissions.newapi import resources

api = Api(api_name='0.1')

for model in (resources.SubmissionSetResource,
              resources.CategorySubmissionResource,
              resources.SubcategorySubmissionResource,
              resources.CreditSubmissionResource,
              ):
    api.register(model())

urlpatterns = api.urls
