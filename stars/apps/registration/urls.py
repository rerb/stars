from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    'stars.apps.registration.views',
    
    (r'^$', 'reg_select_institution'),
    (r'^step1/$', 'reg_select_institution'),
    (r'^step2/$', 'reg_contact_info'),
    (r'^step3/$', 'reg_payment'),
    (r'^account/$', 'reg_account'),
)

# urlpatterns += patterns('django.views.generic.simple',
#     (r'^terms-of-service/$', 'direct_to_template', {'template': 'registration/terms_of_service.html'}),
# )
