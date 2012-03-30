import os, sys

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

import aashe_rules
aashe_rules.autodiscover()

from tastypie.api import Api
from stars.apps.submissions.api import SubmissionSetResource, SummaryPieChart, CategoryPieChart, SubategoryPieChart

v1_api = Api(api_name='v1')
v1_api.register(SubmissionSetResource())
v1_api.register(SummaryPieChart())
v1_api.register(CategoryPieChart())
v1_api.register(SubategoryPieChart())

handler500 = 'stars.apps.helpers.views.server_error'

urlpatterns = patterns('',
                       
    (r'^api/', include(v1_api.urls)),

    # tool:
    #(r'^$', 'stars.apps.tool.views.stars_home_page'),
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
    (r'^tool/$', 'stars.apps.tool.views.tool_dashboard'),
    (r'^tool/credit-editor/', include('stars.apps.tool.credit_editor.urls')),
    (r'^tool/admin/', include('stars.apps.tool.admin.urls')),
    (r'^tool/submissions/', include('stars.apps.tool.my_submission.urls')),
    (r'^tool/my-resources/', include('stars.apps.tool.my_resources.urls')),
    (r'^tool/manage/', include('stars.apps.tool.manage.urls')),
    # articles (cms):
    (r'^'+settings.ARTICLE_PATH_ROOT+'/', include('stars.apps.cms.urls')),

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

    # rules
    #(r'^rules/', include('aashe_rules.urls')),

    # testing / debug / data migration scripts - these urls should normally be commented out!
    #(r'^migrate_required/$', 'stars.apps.helpers.views.migrate_doc_field_required'),
    #(r'^test/$', 'stars.apps.helpers.views.test'),

)

if settings.STANDALONE_MODE:
    urlpatterns += patterns('',
        # static_media
        (r'^media/static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), "static")}),
        # tiny_mce
        (r'^media/tp/js/tiny_mce/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), "../parts/tinyMCE/tinymce/jscripts/tiny_mce/")}),
        # uploads and others
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )


import logging
from sorl.thumbnail.log import ThumbnailLogHandler

handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)