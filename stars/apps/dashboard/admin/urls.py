from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.dashboard.admin.views',
    
    (r'^$', 'institutions'),
    (r'^gateway/find-institution/(?P<snippet>[\d\w\- ]+)$', 'find_institution_gateway'),
    (r'^institution/(?P<institution_id>\d+)/$', 'select_institution'),
    (r'^watchdog/',  include('stars.apps.dashboard.admin.watchdog.urls')),
    (r'^pages/$', 'articles'),
    url(r'pages/syncdb/$', 'article_category_sync', None, name="article-category-sync"),
)