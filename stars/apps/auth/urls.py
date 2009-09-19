from django.conf.urls.defaults import *

# Django Docs:
# http://docs.djangoproject.com/en/dev/topics/auth/

urlpatterns = patterns(
    '',
    
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'auth/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    
    (r'^select-school/(?P<institution_id>\d+)/$', 'stars.apps.auth.views.select_school'),
)
