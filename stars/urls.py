import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

import aashe_rules
aashe_rules.autodiscover()

from stars.apps.helpers.old_path_preserver import (OldPathPreserverView,
                                                   OLD_PATHS_TO_PRESERVE)

handler403 = 'stars.apps.helpers.views.permission_denied'
handler500 = 'stars.apps.helpers.views.server_error'


urlpatterns = patterns('',
    # catch old paths we need to preserve first:
    url(r'^{old_paths_to_preserve}$'.format(
            old_paths_to_preserve='|'.join(OLD_PATHS_TO_PRESERVE)),
        OldPathPreserverView.as_view(), name='old-path-preserver'),

    # api:
    (r'^api/', include('stars.apps.api.urls')),
    (r'^api/', include('stars.apps.submissions.urls')),
    # tool:
    #(r'^$', 'stars.apps.tool.views.stars_home_page'),
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
    # articles (cms):
    (r'^'+settings.ARTICLE_PATH_ROOT+'/', include('stars.apps.cms.urls')),

    # tool
    (r'^tool/', include('stars.apps.tool.urls')),

    # accounts:
    (r'^accounts/', include('stars.apps.accounts.urls')),

    # admin
    (r'^_ad/', include(admin.site.urls)),

    # admin
    (r'^notifications/', include('stars.apps.notifications.urls')),

    # institutions
    (r'^institutions/', include('stars.apps.institutions.urls')),

    # registration
    (r'^register/', include('stars.apps.registration.urls')),

    # custom forms
    (r'^cfm/', include('stars.apps.custom_forms.urls')),
)

if settings.STANDALONE_MODE:
    urlpatterns += patterns('',
        # static_media
        (r'^media/static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), "static")}),
        # tiny_mce
        (r'^media/tp/js/tiny_mce/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), "../parts/tinyMCE/tinymce/jscripts/tiny_mce/")}),

        (r'^media/tp/js/d3/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), "../parts/d3.js/mbostock-d3-224acae/")}),
        # uploads and others
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^styles/$', 'django.views.generic.simple.direct_to_template', {'template': 'styles.html'}),
    )

if settings.PROFILE:
    urlpatterns += patterns('',
                            url(r'^profiler/', include('profiler.urls')))

import logging
from sorl.thumbnail.log import ThumbnailLogHandler

handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)
