from django.conf.urls.defaults import patterns, url

from views import (ArticleDetailView, OldPathRedirectView)

urlpatterns = patterns('',

    # url(r'^(?P<article_slug>[^\/]+).html$',
    #     ArticleDetailView.as_view(),
    #     name='cms-article-detail'),

    url(r'^[^\/]+/(?P<nid>\d+)/$',
        OldPathRedirectView.as_view(),
        name='cms-old-path-redirect'),

    url(r'^(?P<category_slug>[^\/]+)/(?P<article_slug>[^\/]+).html$',
        ArticleDetailView.as_view(),
        name='cms-article-detail'),
)
