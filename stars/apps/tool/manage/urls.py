from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.tool.manage.views',
    
    (r'^$', 'institution_detail'),
    (r'^payments/$', 'institution_payments'),
    (r'^responsible-parties/$', 'responsible_party_list'),
    (r'^responsible-parties/add/$', 'add_responsible_party'),
    (r'^responsible-parties/(?P<rp_id>\d+)/$', 'edit_responsible_party'),
    (r'^responsible-parties/(?P<rp_id>\d+)/delete/$', 'delete_responsible_party'),
    (r'^users/$', 'accounts'),
    (r'^users/add/$', 'add_account'),
    (r'^users/edit/(?P<account_id>\d+)/$', 'accounts'),
    (r'^users/delete/(?P<account_id>\d+)/$', 'delete_account'),
    (r'^submissionsets/$', 'submissionsets'),
    (r'^submissionsets/purchase/$', 'purchase_submissionset'),
    (r'^submissionsets/add/$', 'add_submissionset'),
    (r'^submissionsets/(?P<set_id>\d+)/$', 'edit_submissionset'),
    (r'^submissionsets/(?P<set_id>\d+)/migrate/$', 'migrate_submissionset'),
    (r'^submissionsets/(?P<set_id>\d+)/pay/$', 'pay_submissionset'),
    (r'^submissionsets/(?P<set_id>\d+)/extension/$', 'extension_request'),
    (r'^submissionsets/(?P<set_id>\d+)/activate/$', 'activate_submissionset'),
    (r'^submissionsets/(?P<set_id>\d+)/boundary/$', 'boundary'),
)
