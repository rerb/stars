from django.conf.urls.defaults import patterns, url
from views import InstitutionList, AddSubscriptionPayment, EditSubscriptionPayment

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
    url(r'^payments/(?P<institution_slug>[^/]+)/(?P<subscription_id>\d+)/(?P<payment_id>\d+)/$',
        EditSubscriptionPayment.as_view(),
        name="edit_payment"),

    url(r'^payments(?P<institution_slug>[^/]+)/(?P<subscription_id>\d+)/add/$',
        AddSubscriptionPayment.as_view(),
        name="add_payment"),

#     (r'^payments/$', 'latest_payments'),
#    (r'^payments/(?P<payment_id>\d+)/edit/$', 'edit_payment'),
#    (r'^payments/(?P<payment_id>\d+)/receipt/$', 'send_receipt'),
#    (r'^payments/(?P<payment_id>\d+)/delete/$', 'delete_payment'),
)
