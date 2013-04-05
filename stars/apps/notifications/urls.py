from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from stars.apps.notifications.views import *

urlpatterns = patterns(
    'stars.apps.registration.views',
    
    (r'^preview/(?P<slug>[^/]+)/$', PreviewEmailTemplate.as_view())
)
