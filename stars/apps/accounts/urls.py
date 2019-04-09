from django.conf.urls import url
from django.contrib.auth.views import login, logout_then_login
from longerusernameandemail.forms import AuthenticationForm


urlpatterns = [
    url(r'^login/$', login,
        {'authentication_form': AuthenticationForm}, name='login'),
    url(r'^logout/$', logout_then_login, name='logout'),
]
