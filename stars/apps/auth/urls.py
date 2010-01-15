from django.conf.urls.defaults import *

# Django Docs:
# http://docs.djangoproject.com/en/dev/topics/auth/

urlpatterns = patterns(
    '',
    
    #(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'auth/login.html'}),
    (r'^login/$', 'stars.apps.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    
    # Terms of Service
    (r'^tos/$', 'stars.apps.auth.views.terms_of_service'),
    
    (r'^select-school/(?P<institution_id>\d+)/$', 'stars.apps.auth.views.select_school'),
)
