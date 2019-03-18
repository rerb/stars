from django.conf.urls import patterns, url
from stars.apps.custom_forms.views import DataDisplaysAccessRequestView

urlpatterns = patterns(
    'stars.apps.custom_forms.views',

    url(r'dd-access/$', DataDisplaysAccessRequestView.as_view(),
        name='dd-access-request'),
)
