import logging

import logical_rules
from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib import admin
from longerusernameandemail.forms import AuthenticationForm
from sorl.thumbnail.log import ThumbnailLogHandler

from stars.apps.helpers.old_path_preserver import (OldPathPreserverView,
                                                   OLD_PATHS_TO_PRESERVE)
from stars.apps.old_cms.views import (HomePageView)

logical_rules.autodiscover()

handler403 = 'stars.apps.helpers.views.permission_denied'
handler500 = 'stars.apps.helpers.views.server_error'

urlpatterns = [

    # catch old paths we need to preserve first:
    url(r'^{old_paths_to_preserve}$'.format(
        old_paths_to_preserve='|'.join(OLD_PATHS_TO_PRESERVE)),
        OldPathPreserverView.as_view(), name='old-path-preserver'),

    # api:
    url(r'^api/', include('stars.apps.api.urls')),
    url(r'^api/', include('stars.apps.submissions.urls')),
    # tool:
    # (r'^$', 'stars.apps.tool.views.stars_home_page'),
    url(r'^$', HomePageView.as_view(), {'template_name': 'home.html'}),

    # articles (cms):
    url(r'^pages/', include('stars.apps.old_cms.urls')),

    # tool
    url(r'^tool/', include('stars.apps.tool.urls')),

    # accounts:
    url(r'^accounts/login/$',
        'django.contrib.auth.views.login',
        {'authentication_form': AuthenticationForm}),

    url(r'^accounts/logout',
        'django.contrib.auth.views.logout_then_login'),
    # ('^accounts/', include('django.contrib.auth.urls')),

    # admin
    url(r'^_ad/', include(admin.site.urls)),

    # admin
    url(r'^notifications/', include('stars.apps.notifications.urls')),

    # institutions
    url(r'^institutions/', include('stars.apps.institutions.urls')),

    # third parties
    url(r'^tp/', include('stars.apps.third_parties.urls')),

    # registration
    url(r'^register/', include('stars.apps.registration.urls')),

    # custom forms
    url(r'^cfm/', include('stars.apps.custom_forms.urls')),

    # url(r'^new-pages/', include('cms.urls')),

    # djcelery
    url('^tasks/', include('djcelery.urls')),

    # django-terms
    url(r'^terms/', include('terms.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.extend([
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^styles/$', TemplateView.as_view(template_name='styles.html'), name="styles")
    ])

if settings.DEBUG:
    urlpatterns.extend([
        url(r'^media/(?P<path>.*)$',
            'django.views.static.serve', {
                'document_root':
                settings.MEDIA_ROOT,
            }),
    ])

if settings.PROFILE:
    urlpatterns.extend([url(r'^profiler/', include('profiler.urls')), ])

handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)
