from django.conf.urls.defaults import patterns

from stars.apps.cms.views import ArticleDetailView, CategoryDetailView, \
     OldPathRedirectView, SubcategoryDetailView

urlpatterns = patterns('stars.apps.cms.views',

    (r'^(?P<category_slug>[^\/]+)/$', CategoryDetailView.as_view()),

    (r'^[^\/]+/(?P<nid>\d+)/$', OldPathRedirectView.as_view()),

    (r'^(?P<category_slug>[^\/]+)/(?P<article_slug>[^\/]+).html$',
     ArticleDetailView.as_view()),

    (r'^(?P<category_slug>[^\/]+)/(?P<subcategory_slug>[^\/]+)/$',
     SubcategoryDetailView.as_view()),

    (r'^(?P<category_slug>[^\/]+)/(?P<subcategory_slug>[^\/]+)/(?P<article_slug>[^\/]+).html$',
     ArticleDetailView.as_view()),

)
