import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

import logical_rules
logical_rules.autodiscover()

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
#    (r'^accounts/', include('stars.apps.accounts.urls')),
    ('^accounts/', include('aashe.aasheauth.urls')),

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

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^styles/$', 'django.views.generic.simple.direct_to_template', {'template': 'styles.html'}),
    )

import logging
from sorl.thumbnail.log import ThumbnailLogHandler

handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)
