from django.conf.urls.defaults import *
from stars.apps.cms.models import Article

urlpatterns = patterns('stars.apps.cms.views',
    
    (r'^(?P<category_slug>[^\/]+)/$', 'category_detail'),
    (r'^(?P<category_slug>[^\/]+)/(?P<article_slug>[^\/]+).html$', 'article_detail'),
    (r'^(?P<category_slug>[^\/]+)/(?P<subcategory_slug>[^\/]+)/$', 'subcategory_detail'),
    (r'^(?P<category_slug>[^\/]+)/(?P<subcategory_slug>[^\/]+)/(?P<article_slug>[^\/]+).html$', 'article_detail'),
)