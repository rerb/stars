from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'stars.apps.tool.views.tool_dashboard'),
    (r'^credit-editor/', include('stars.apps.tool.credit_editor.urls')),
    (r'^admin/', include('stars.apps.tool.admin.urls')),
    (r'^submissions/', include('stars.apps.tool.my_submission.urls')),
    (r'^my-resources/', include('stars.apps.tool.my_resources.urls')),
    (r'^(?P<institution_slug>[^/]*)/manage/', include('stars.apps.tool.manage.urls')),
)