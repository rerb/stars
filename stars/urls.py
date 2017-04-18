import logging

import logical_rules
from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from longerusernameandemail.forms import AuthenticationForm
from sorl.thumbnail.log import ThumbnailLogHandler

from stars.apps.helpers.old_path_preserver import (OldPathPreserverView,
                                                   OLD_PATHS_TO_PRESERVE)
from stars.apps.old_cms.views import (HomePageView)


admin.autodiscover()
logical_rules.autodiscover()

handler403 = 'stars.apps.helpers.views.permission_denied'
handler500 = 'stars.apps.helpers.views.server_error'

urlpatterns = patterns(
    '',

    # catch old paths we need to preserve first:
    url(r'^{old_paths_to_preserve}$'.format(
            old_paths_to_preserve='|'.join(OLD_PATHS_TO_PRESERVE)),
        OldPathPreserverView.as_view(), name='old-path-preserver'),

    # api:
    (r'^api/', include('stars.apps.api.urls')),
    (r'^api/', include('stars.apps.submissions.urls')),
    # tool:
    # (r'^$', 'stars.apps.tool.views.stars_home_page'),
    (r'^$', HomePageView.as_view(), {'template_name': 'home.html'}),

    # articles (cms):
    (r'^pages/', include('stars.apps.old_cms.urls')),

    # tool
    (r'^tool/', include('stars.apps.tool.urls')),

    # accounts:
    (r'^accounts/login/$',
     'django.contrib.auth.views.login',
     {'authentication_form': AuthenticationForm}),

    ('^accounts/', include('django.contrib.auth.urls')),

    # admin
    (r'^_ad/', include(admin.site.urls)),

    # admin
    (r'^notifications/', include('stars.apps.notifications.urls')),

    # institutions
    (r'^institutions/', include('stars.apps.institutions.urls')),

    # third parties
    (r'^tp/', include('stars.apps.third_parties.urls')),

    # registration
    (r'^register/', include('stars.apps.registration.urls')),

    # custom forms
    (r'^cfm/', include('stars.apps.custom_forms.urls')),

    # url(r'^new-pages/', include('cms.urls')),

    # djcelery
    url('^tasks/', include('djcelery.urls')),

    # django-terms
    url(r'^terms/', include('terms.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^styles/$',
         'django.views.generic.simple.direct_to_template',
         {'template': 'styles.html'}),
    )

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$',
            'django.views.static.serve', {
                'document_root':
                settings.MEDIA_ROOT,
            }),
    )

if settings.PROFILE:
    urlpatterns += patterns('',
                            url(r'^profiler/', include('profiler.urls')))

handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)
