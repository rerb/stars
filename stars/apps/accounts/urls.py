from django.conf.urls.defaults import patterns, url

# Django Docs:
# http://docs.djangoproject.com/en/dev/topics/auth/

urlpatterns = patterns(
    '',

    #(r'^login/$', 'django.contrib.accounts.views.login', {'template_name': 'auth/login.html'}),
    (r'^login/$', 'stars.apps.accounts.views.login_view'),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),

    # Terms of Service
    (r'^tos/$', 'stars.apps.accounts.views.terms_of_service'),

    url(r'^select-school/(?P<institution_id>\d+)/$',
        'stars.apps.accounts.views.select_school',
        name='select-school'),
)
