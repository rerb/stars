from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from stars.apps.institutions.data_displays.views import *

urlpatterns = patterns(
    'django.views.generic.simple',
    # data views
    (r'^$', "direct_to_template",{'template': 'institutions/data_views/index.html'}),
    (r'^dashboard/$', Dashboard.as_view()),
    (r'^categories/$', AggregateFilter.as_view()),
)