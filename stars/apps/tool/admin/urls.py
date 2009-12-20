from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.tool.admin.views',
    
    # Institutional Admin
    (r'^$', 'institutions_list'),
    (r'^search/$', 'institutions_search'),
    (r'^list$', 'institutions_list'),
    # The snippet for the gateway URL is filtered by the JS search_institution() ajax - see ticket #220
    # Ideally, these two regular expressions should match opposite patterns.
    (r'^gateway/find-institution/(?P<snippet>[\d\w\-\. ]+)$', 'find_institution_gateway'),
    (r'^institution/masquerade/(?P<aashe_id>\d+)/$', 'select_institution'),

    # Payment processing
    (r'^institution/(?P<institution_id>\d+)/payments/$', 'institution_payments'),
    (r'^institution/(?P<institution_id>\d+)/submissionsets/(?P<submissionset_id>\d+)/add-payment/$', 'add_payment'),
    (r'^payments/$', 'latest_payments'),
    (r'^payments/(?P<payment_id>\d+)/edit/$', 'edit_payment'),
    (r'^payments/(?P<payment_id>\d+)/delete/$', 'delete_payment'),

    # Admin utilities
    (r'^watchdog/',  include('stars.apps.tool.admin.watchdog.urls')),
    (r'^pages/$', 'articles'),
    url(r'pages/syncdb/$', 'article_category_sync', None, name="article-category-sync"),
)
