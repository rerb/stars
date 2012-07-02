from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.tool.admin.views',
    
    # Institutional Admin
    (r'^$', 'institutions_list'),
    (r'^search/$', 'institutions_search'),
    (r'^list$', 'institutions_list'),
    (r'^institution/masquerade/(?P<id>\d+)/$', 'select_institution'),
    
    # Reports
    (r'^reports/$', 'overview_report'),

    # Payment processing
    (r'^institution/(?P<institution_id>\d+)/payments/$', 'institution_payments'),
    (r'^institution/(?P<institution_id>\d+)/submissionsets/(?P<submissionset_id>\d+)/add-payment/$', 'add_payment'),
    (r'^payments/$', 'latest_payments'),
    (r'^payments/(?P<payment_id>\d+)/edit/$', 'edit_payment'),
    (r'^payments/(?P<payment_id>\d+)/receipt/$', 'send_receipt'),
    (r'^payments/(?P<payment_id>\d+)/delete/$', 'delete_payment'),

    # Admin utilities
    (r'^watchdog/',  include('stars.apps.tool.admin.watchdog.urls')),
)
