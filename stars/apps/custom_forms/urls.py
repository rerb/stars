from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.custom_forms.views',
    
    (r'ta-app/$', 'ta_application'),
    (r'sc-app/$', 'sc_application'),
    (r'eligibility-inquiry/$', 'eligibility')
)
