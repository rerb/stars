from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.tool.my_resources.views',
    
    (r'^$', 'my_resources'),
)
