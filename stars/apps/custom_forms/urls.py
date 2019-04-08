from django.conf.urls import url
from stars.apps.custom_forms.views import DataDisplaysAccessRequestView

urlpatterns = [
    url(r'dd-access/$', DataDisplaysAccessRequestView.as_view(),
        name='dd-access-request'),
]
