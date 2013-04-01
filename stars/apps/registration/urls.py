from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

from views import SurveyView

urlpatterns = patterns(
    'stars.apps.registration.views',

    url(r'^$', 'participant_reg', name='registration'),

    url(r'^(?P<institution_slug>[^/]*)/survey/$', SurveyView.as_view(), name='reg_survey')

)
