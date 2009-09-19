from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.dashboard.admin.watchdog.views',
    
    (r'^$', 'list'),
    (r'^(?P<entry_id>\d+)/$', 'detail'),
    (r'^purge/',  'purge'),
)