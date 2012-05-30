from tastypie.api import Api

from stars.apps.submissions.api import CategoryPieChart, SubategoryPieChart, \
     SummaryPieChart


v1_api = Api(api_name='v1')
v1_api.register(CategoryPieChart())
v1_api.register(SubategoryPieChart())
#v1_api.register(SubmissionSetResource())
v1_api.register(SummaryPieChart())

urlpatterns = v1_api.urls
