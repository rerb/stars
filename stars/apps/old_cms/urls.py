from django.conf.urls.defaults import patterns, url

from views import (ArticleDetailView,
                   # ArticleDetailWithFacebookCommentsWidgetView,
                   OldPathRedirectView)

urlpatterns = patterns(
    '',

    url(r'^[^\/]+/(?P<nid>\d+)/$',
        OldPathRedirectView.as_view(),
        name='cms-old-path-redirect'),

    # # 'cms-article-detail-with-facebook-comment-widget' must come
    # # before 'cms-article-detail'.  Otherwise, 'cms-article-detail'
    # # will eat patterns before they get to
    # # 'cms-article-detail-with-facebook-comment-widget'.
    # url(r'^(?P<category_slug>about)/(?P<article_slug>2016-sustainable-campus-index).html$',  # noqa
    #     ArticleDetailWithFacebookCommentsWidgetView.as_view(),
    #     name='cms-article-detail-with-facebook-comment-widget'),

    url(r'^(?P<category_slug>[^\/]+)/(?P<article_slug>[^\/]+).html$',
        ArticleDetailView.as_view(),
        name='cms-article-detail')
)
