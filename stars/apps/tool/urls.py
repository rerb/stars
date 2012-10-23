from django.conf.urls.defaults import include, patterns, url

from stars.apps.tool.views import SummaryToolView

urlpatterns = patterns('',
    (r'^credit-editor/', include('stars.apps.tool.credit_editor.urls')),
    (r'^admin/', include('stars.apps.tool.admin.urls')),
    (r'^submissions/', include('stars.apps.tool.my_submission.urls')),
    (r'^my-resources/', include('stars.apps.tool.my_resources.urls')),
    url(r'^(?P<institution_slug>[^/]*)/$', SummaryToolView.as_view(),
        name='tool-summary'),
    (r'^(?P<institution_slug>[^/]*)/manage/',
     include('stars.apps.tool.manage.urls')),
)
