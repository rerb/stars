from django.conf.urls import patterns, url
from stars.apps.custom_forms.views import (EligibilityView,
                                           SteeringCommitteeNominationView,
                                           TechnicalAdvisorApplicationView,
                                           DataDisplaysAccessRequestView)

urlpatterns = patterns(
    'stars.apps.custom_forms.views',

    url(r'ta-app/$', TechnicalAdvisorApplicationView.as_view(),
        name='technical-advisor-application'),
    url(r'sc-app/$', SteeringCommitteeNominationView.as_view(),
        name='steering-committee-nomination'),
    url(r'eligibility-inquiry/$', EligibilityView.as_view(),
        name='eligibility-inquiry'),
    url(r'dd-access/$', DataDisplaysAccessRequestView.as_view(),
        name='dd-access-request'),
)
