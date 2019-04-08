from django.conf.urls import url

from stars.apps.notifications.views import *

urlpatterns = [
    url(r'^preview/(?P<slug>[^/]+)/$', PreviewEmailTemplate.as_view())
]
