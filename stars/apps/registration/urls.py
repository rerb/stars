from django.conf.urls.defaults import patterns, url

from .views import (BasicAccessRegistrationWizard,
                    FullAccessRegistrationWizard,
                    SurveyView,
                    InstitutionCreateView)

urlpatterns = patterns(
    'stars.apps.registration.views',

    url(r'^$', InstitutionCreateView.as_view(), name='institution-create'),

    url(r'^basic-access/$',
        BasicAccessRegistrationWizard.as_view(
            BasicAccessRegistrationWizard.get_class_form_list(),
            condition_dict=BasicAccessRegistrationWizard.get_form_conditions()
        ),
        name='basic-access-registration'),

    url(r'^full-access/$',
        FullAccessRegistrationWizard.as_view(
            FullAccessRegistrationWizard.get_class_form_list(),
            condition_dict=FullAccessRegistrationWizard.get_form_conditions()
        ),
        name='full-access-registration'),

    url(r'^(?P<institution_slug>[^/]*)/survey/$',
        SurveyView.as_view(),
        name='reg_survey')
)
