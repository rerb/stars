from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import (RegistrationWizard,
                    SurveyView,
                    InstitutionCreateView)

urlpatterns = patterns(
    'stars.apps.registration.views',

    url(r'^$',
        login_required(InstitutionCreateView.as_view()),
        name='institution-create'),

    url(r'^wizard/$',
        RegistrationWizard.as_view(
            RegistrationWizard.get_class_form_list(),
            condition_dict={}
        ),
        name='registration-wizard'),

    url(r'^(?P<institution_slug>[^/]*)/survey/$',
        SurveyView.as_view(),
        name='reg_survey')
)
