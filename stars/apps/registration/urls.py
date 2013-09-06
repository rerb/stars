from django.conf.urls.defaults import patterns, url

from .views import RegistrationWizard, SurveyView

urlpatterns = patterns(
    'stars.apps.registration.views',

    url(r'^$',
        RegistrationWizard.as_view(
            RegistrationWizard.get_class_form_list(),
            condition_dict=RegistrationWizard.get_form_conditions()),
        name='registration'),

    url(r'^(?P<institution_slug>[^/]*)/survey/$',
        SurveyView.as_view(),
        name='reg_survey')
)
