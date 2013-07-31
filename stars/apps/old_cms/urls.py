from django.conf.urls.defaults import patterns, url

from views import (ArticleDetailView, CategoryDetailView,
                   OldPathRedirectView, SubcategoryDetailView)

urlpatterns = patterns('',

    url(r'^(?P<category_slug>[^\/]+)/$',
        CategoryDetailView.as_view(),
        name='cms-category-detail'),

    url(r'^[^\/]+/(?P<nid>\d+)/$',
        OldPathRedirectView.as_view(),
        name='cms-old-path-redirect'),

    url(r'^(?P<category_slug>[^\/]+)/(?P<article_slug>[^\/]+).html$',
        ArticleDetailView.as_view(),
        name='cms-article-detail'),

    url(r'^(?P<category_slug>[^\/]+)/(?P<subcategory_slug>[^\/]+)/$',
        SubcategoryDetailView.as_view(),
        name='cms-subcategory-detail'),

    url(r'^(?P<category_slug>[^\/]+)/(?P<subcategory_slug>[^\/]+)/(?P<article_slug>[^\/]+).html$',
        ArticleDetailView.as_view(),
        name='cms-article-detail'),

)
