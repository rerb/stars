from django.conf.urls.defaults import *

from stars.apps.notifications.views import *

urlpatterns = patterns(
    'stars.apps.registration.views',

    (r'^preview/(?P<slug>[^/]+)/$', PreviewEmailTemplate.as_view())
)
