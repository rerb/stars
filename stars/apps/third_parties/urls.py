from django.conf.urls.defaults import *
from stars.apps.third_parties.views import SnapshotList

urlpatterns = patterns(
    'stars.apps.third_parties.views',

    (r'^(?P<slug>[^/]+)/$', SnapshotList.as_view()),
)
