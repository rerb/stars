from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

handler500 = 'stars.apps.helpers.views.server_error'

urlpatterns = patterns('',
    # dashboard:
    (r'^$', 'stars.apps.dashboard.views.stars_home_page'),
    (r'^dashboard/$', 'stars.apps.dashboard.views.dashboard'),
    (r'^dashboard/credit-editor/', include('stars.apps.dashboard.credit_editor.urls')),
    (r'^dashboard/admin/', include('stars.apps.dashboard.admin.urls')),
    (r'^dashboard/submissions/', include('stars.apps.dashboard.submissions.urls')),
    (r'^dashboard/manage/', include('stars.apps.dashboard.manage.urls')),
    # articles (cms):
    (r'^'+settings.ARTICLE_PATH_ROOT+'/', include('stars.apps.cms.urls')),

    # auth:
    (r'^auth/', include('stars.apps.auth.urls')),

    # admin
    (r'^admin/(.*)', admin.site.root),
    
    # institutions
    (r'^institutions/$', 'stars.apps.institutions.views.institutions'),    

    # registration
    (r'^register/', include('stars.apps.registration.urls')),

    # testing / debug / data migration scripts - these urls should normally be commented out!
    (r'^migrate_required/$', 'stars.apps.helpers.views.migrate_doc_field_required'),
    #(r'^test/$', 'stars.apps.helpers.views.test'),

)

if settings.STANDALONE_MODE:
    urlpatterns += patterns('',
    # media
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
