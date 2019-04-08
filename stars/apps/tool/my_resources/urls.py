from django.conf.urls import url

from views import MyResourcesView

urlpatterns = [
    url(r'^$', MyResourcesView.as_view(), name='my-resources'),
]
