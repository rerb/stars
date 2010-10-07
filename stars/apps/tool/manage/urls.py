from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.tool.manage.views',
    
    (r'^$', 'institution_detail'),
    (r'^payments/$', 'institution_payments'),
    (r'^users/$', 'accounts'),
    (r'^users/add/$', 'add_account'),
    (r'^users/edit/(?P<account_id>\d+)/$', 'accounts'),
    (r'^users/delete/(?P<account_id>\d+)/$', 'delete_account'),
    (r'^submissionsets/$', 'submissionsets'),
    (r'^submissionsets/add/$', 'add_submissionset'),
    (r'^submissionsets/(?P<set_id>\d+)/$', 'edit_submissionset'),
    (r'^submissionsets/(?P<set_id>\d+)/activate/$', 'activate_submissionset'),
    (r'^submissionsets/(?P<set_id>\d+)/boundary/$', 'boundary'),
)
