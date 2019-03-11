from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import SurveyView, InstitutionCreateView

urlpatterns = patterns(
    'stars.apps.registration.views',

    url(r'^$',
        login_required(InstitutionCreateView.as_view()),
        name='institution-create'),

    url(r'^(?P<institution_slug>[^/]*)/survey/$',
        SurveyView.as_view(),
        name='reg_survey')
)
