import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

handler500 = 'stars.apps.helpers.views.server_error'

urlpatterns = patterns('',
    # tool:
    #(r'^$', 'stars.apps.tool.views.stars_home_page'),
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
    (r'^tool/$', 'stars.apps.tool.views.tool'),
    (r'^tool/credit-editor/', include('stars.apps.tool.credit_editor.urls')),
    (r'^tool/admin/', include('stars.apps.tool.admin.urls')),
    (r'^tool/submissions/', include('stars.apps.tool.submissions.urls')),
    (r'^tool/my-resources/', include('stars.apps.tool.my_resources.urls')),
    (r'^tool/manage/', include('stars.apps.tool.manage.urls')),
    # articles (cms):
    (r'^'+settings.ARTICLE_PATH_ROOT+'/', include('stars.apps.cms.urls')),

    # auth:
    (r'^auth/', include('stars.apps.auth.urls')),

    # admin
    (r'^_ad/(.*)', admin.site.root),
    
    # institutions
    (r'^institutions/', include('stars.apps.institutions.urls')),

    # registration
    (r'^register/', include('stars.apps.registration.urls')),
    
    # custom forms
    (r'^cfm/', include('stars.apps.custom_forms.urls')),

    # testing / debug / data migration scripts - these urls should normally be commented out!
    #(r'^migrate_required/$', 'stars.apps.helpers.views.migrate_doc_field_required'),
    #(r'^test/$', 'stars.apps.helpers.views.test'),

)

if settings.STANDALONE_MODE:
    urlpatterns += patterns('',
    # media
        (r'^media/static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), "static")}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
