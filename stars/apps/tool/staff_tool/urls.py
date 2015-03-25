from django.conf.urls.defaults import patterns, url
from django.views.decorators.cache import never_cache

from views import (
    InstitutionList,
    AddSubscriptionPayment,
    EditSubscriptionPayment,
    AccrualReport,
    AccrualExcelView,
    AccrualExcelDownloadView)

urlpatterns = patterns(
    'stars.apps.tool.staff_tool.views',

    # Institutional Admin
    (r'^$', InstitutionList.as_view()),
    (r'^search/$', 'institutions_search'),
    (r'^list$', InstitutionList.as_view()),
    (r'^institution/masquerade/(?P<id>\d+)/$', 'select_institution'),

    # Reports
    (r'^reports/$', 'overview_report'),
    (r'^reports/financials/$', 'financial_report'),
    (r'^reports/accrual/$', AccrualReport.as_view()),

    # Report Export Views
    url(r'^reports/accrual/csv/(?P<year>\d+)/$',
        never_cache(AccrualExcelView.as_view()),
        name='accrual_modal'),
    url(r'^reports/accrual/csv/(?P<year>\d+)/download/(?P<task>[^/]+)/$',
        never_cache(AccrualExcelDownloadView.as_view()),
        name='accrual_download'),

    # Payment processing
    url(r'^payments/(?P<institution_slug>[^/]+)/(?P<subscription_id>\d+)/(?P<payment_id>\d+)/$',
        EditSubscriptionPayment.as_view(),
        name="edit_payment"),

    url(r'^payments/(?P<institution_slug>[^/]+)/(?P<subscription_id>\d+)/add/$',
        AddSubscriptionPayment.as_view(),
        name="add_payment"),

#     (r'^payments/$', 'latest_payments'),
#    (r'^payments/(?P<payment_id>\d+)/edit/$', 'edit_payment'),
#    (r'^payments/(?P<payment_id>\d+)/receipt/$', 'send_receipt'),
#    (r'^payments/(?P<payment_id>\d+)/delete/$', 'delete_payment'),
)
