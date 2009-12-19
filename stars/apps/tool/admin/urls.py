from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.tool.admin.views',
    
    (r'^$', 'institutions_list'),
    (r'^search/$', 'institutions_search'),
    (r'^list$', 'institutions_list'),
    # The snippet for the gateway URL is filtered by the JS search_institution() ajax - see ticket #220
    # Ideally, these two regular expressions should match opposite patterns.
    (r'^gateway/find-institution/(?P<snippet>[\d\w\-\. ]+)$', 'find_institution_gateway'),
    (r'^institution/(?P<institution_id>\d+)/$', 'select_institution'),
    (r'^watchdog/',  include('stars.apps.tool.admin.watchdog.urls')),
    (r'^pages/$', 'articles'),
    url(r'pages/syncdb/$', 'article_category_sync', None, name="article-category-sync"),
)
