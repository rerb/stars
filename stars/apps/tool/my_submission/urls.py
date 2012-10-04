from django.conf.urls.defaults import *
from stars.apps.tool.my_submission.views import EditBoundaryView, SaveSnapshot, ConfirmClassView

urlpatterns = patterns(
    'stars.apps.tool.my_submission.views',

    (r'^$', 'summary'),
    (r'^boundary/$', EditBoundaryView.as_view()),
    (r'^add-responsible-party/$', 'add_responsible_party'),
#    (r'^(?P<category_id>\d+)/$', 'category_detail'),
    (r'^(?P<category_id>\d+)/(?P<subcategory_id>\d+)/$', 'subcategory_detail'),
    (r'^(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/$', 'credit_detail'),
    (r'^(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/documentation/$', 'credit_documentation'),
    (r'^(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/notes/$', 'credit_notes'),
    # uploaded file access
    (r'^my_uploads/secure/(?P<inst_id>\d+)/(?P<path>.+)$', 'serve_uploaded_file'),

    # Submit for Rating
    #(r'^submit/$', 'submit_for_rating'),
    url(r'^snapshot/$', SaveSnapshot.as_view(), name='save-snapshot'),
    (r'^submit/$', ConfirmClassView.as_view()),
    # (r'^submit/status/', 'submit_status'),
    (r'^submit/letter/$', 'submit_letter'),
    (r'^submit/finalize/$', 'submit_finalize'),
    (r'^gateway/media/secure/(?P<inst_id>\d+)/(?P<creditset_id>\d+)/(?P<credit_id>\d+)/(?P<field_id>\d+)/(?P<filename>[^/]+)/delete/$', 'delete_uploaded_file_gateway'),
)
