from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    'stars.apps.registration.views',
    
    (r'^$', 'reg_select_institution'),
    (r'^step1/$', 'reg_select_institution'),
    (r'^international/$', 'reg_international'),
    (r'^step2/$', 'reg_contact_info'),
    (r'^step3/$', 'select_participation_level'),
    (r'^step4/$', 'reg_payment'),
    (r'^survey/$', 'survey'),
    (r'^account/$', 'reg_account'),
)

# urlpatterns += patterns('django.views.generic.simple',
#     (r'^terms-of-service/$', 'direct_to_template', {'template': 'registration/terms_of_service.html'}),
# )
