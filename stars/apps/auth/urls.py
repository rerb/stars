from django.conf.urls.defaults import *

# Django Docs:
# http://docs.djangoproject.com/en/dev/topics/auth/

urlpatterns = patterns(
    '',
    
    #(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'auth/login.html'}),
    (r'^login/$', 'stars.apps.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    
    (r'^select-school/(?P<institution_id>\d+)/$', 'stars.apps.auth.views.select_school'),
    
    # uploaded file access
    (r'^my_uploads/secure/(?P<inst_id>\d+)/(?P<creditset_id>\d+)/(?P<credit_id>\d+)/(?P<field_id>\d+)/(?P<filename>[^/]+)$', 'stars.apps.auth.views.serve_uploaded_file'),
)
