from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    (r'^login/$', 'stars.apps.accounts.views.login_view'),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),

    url(r'^select-school/(?P<institution_id>\d+)/$',
        'stars.apps.accounts.views.select_school',
        name='select-school'),
)
