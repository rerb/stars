from django.conf.urls.defaults import *
from stars.apps.cms.models import Article

urlpatterns = patterns('stars.apps.cms.views',
    url(r'^(?P<category_slug>[-\w\.& ]+)/(?P<article_id>[-\d]+)/$', 'article_detail', None, name="article-detail"),
    url(r'^(?P<category_slug>[-\w\.& ]+)/$', 'article_list', None, name="article-home"),
)
