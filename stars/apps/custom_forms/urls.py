from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.custom_forms.views',
    
    (r'ta-app/$', 'ta_application'),
)
