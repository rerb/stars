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
    (r'^institution/(?P<institution_id>\d+)/payments/(?P<payment_id>\d+)/$', 'edit_subscriptionpayment'),
    (r'^institution/(?P<institution_id>\d+)/payments/add/(?P<subscription_id>\d+)/$', 'add_subscriptionpayment'),
    (r'^payments/$', 'latest_payments'),
#    (r'^payments/(?P<payment_id>\d+)/edit/$', 'edit_payment'),
#    (r'^payments/(?P<payment_id>\d+)/receipt/$', 'send_receipt'),
#    (r'^payments/(?P<payment_id>\d+)/delete/$', 'delete_payment'),

    # Admin utilities
    (r'^watchdog/',  include('stars.apps.tool.admin.watchdog.urls')),
)
