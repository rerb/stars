from django.conf.urls import url, patterns

from views import MyResourcesView

urlpatterns = patterns(
    '',
    url(r'^$', MyResourcesView.as_view(), name='my-resources'),
)
