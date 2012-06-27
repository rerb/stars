from django.conf.urls.defaults import *

# Django Docs:
# http://docs.djangoproject.com/en/dev/topics/auth/

urlpatterns = patterns(
    '',
    
    #(r'^login/$', 'django.contrib.accounts.views.login', {'template_name': 'auth/login.html'}),
    (r'^login/$', 'stars.apps.accounts.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    
    # Terms of Service
    (r'^tos/$', 'stars.apps.accounts.views.terms_of_service'),
    
    (r'^select-school/(?P<institution_id>\d+)/$', 'stars.apps.accounts.views.select_school'),
)
