from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from stars.apps.institutions.data_displays.views import *

urlpatterns = patterns(
    'django.views.generic.simple',
    # data views
    (r'^$', "direct_to_template",{'template': 'institutions/data_views/index.html'}),
    (r'^dashboard/$', Dashboard.as_view()),
#    (r'^data-views/score/$', "direct_to_template",
#                                    {'template': 'institutions/data_views/score.html',
#                                     'extra_context': {'creditset': creditset}}),
#    (r'^data-views/content/$', "direct_to_template",
#                                    {'template': 'institutions/data_views/content.html',
#                                     'extra_context': {'creditset': creditset}}),
#    (r'^data-views/stats/$', "direct_to_template",
#                                    {'template': 'institutions/data_views/statistics.html',
#                                     'extra_context': {'creditset': creditset}}),
)