from django.conf.urls.defaults import *
from views import InstitutionList

urlpatterns = patterns(
    'stars.apps.tool.admin.views',
    
    # Institutional Admin
    (r'^$', InstitutionList.as_view()),
    (r'^search/$', 'institutions_search'),
    (r'^list$', InstitutionList.as_view()),
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
)
