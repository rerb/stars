from django.conf.urls import url
from django.contrib.auth.views import logout_then_login

from stars.apps.accounts.views import login_view, select_school


urlpatterns = [
    url(r'^login/$', login_view),
    url(r'^logout/$', logout_then_login),
    url(r'^select-school/(?P<institution_id>\d+)/$',
        select_school,
        name='select-school'),
]
