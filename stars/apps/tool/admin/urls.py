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

    # Admin utilities
    (r'^watchdog/',  include('stars.apps.tool.admin.watchdog.urls')),
)
