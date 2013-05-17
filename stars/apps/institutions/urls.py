from django.conf.urls.defaults import *
from django.views.decorators.cache import never_cache

from stars.apps.institutions.views import *

urlpatterns = patterns(
    'stars.apps.institutions.views',

    # Active Institutions
    (r'^$', ActiveInstitutions.as_view()),

    # Rated institutions
    (r'^rated/$', RatedInstitutions.as_view()),

    # Submission Inquiry Form
    url(r'^inquiry/$', SubmissionInquirySelectView.as_view(),
        name='submission-inquiry'),

    # All scorecards for an Institution
    url(r'^(?P<institution_slug>[^/]+)/report/$',
        InstitutionScorecards.as_view(), name='scorecard-list'),

    # Specific scorecard summary for an institution
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/$',
        ScorecardSummary.as_view(), name='scorecard-summary'),

    # Submission inquiry for an institution
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/inquiry/$',
        SubmissionInquiryView.as_view(),
        name='institution-submission-inquiry'),

    # PDF Export of Submission
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/pdf/$', PDFExportView.as_view()),

    # Old Credit Scorecard - all ints for category_id, subcategory_id, and
    # credit_id; redirects to new Credit Scorecard url below:
    (r'^(?P<institution_slug>[^/]+)'
     '/report'
     '/(?P<submissionset>[^/]+)'
     '/(?P<category_id>\d+)'
     '/(?P<subcategory_id>\d+)'
     '/(?P<credit_id>\d+)/$',
     RedirectOldScorecardCreditURLsView.as_view()),

    # Credit Scorecard
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_abbreviation>[^/]+)/(?P<subcategory_slug>[^/]+)/(?P<credit_identifier>[^/]+)/$',
        ScorecardCredit.as_view(),
        name='scorecard-credit'),

    # Data correction request
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_abbreviation>[^/]+)/(?P<subcategory_slug>[^/]+)/(?P<credit_identifier>[^/]+)/(?P<field_id>\d+)/$', DataCorrectionView.as_view()),

    # Credit Documentation
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_abbreviation>[^/]+)/(?P<subcategory_slug>[^/]+)/(?P<credit_identifier>[^/]+)/documentation/$', ScorecardCreditDocumentation.as_view()),

    # Internal Notes
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_abbreviation>[^/]+)/(?P<subcategory_slug>[^/]+)/(?P<credit_identifier>[^/]+)/internal-notes/$', ScorecardInternalNotesView.as_view()),

    (r'^data-displays/', include('stars.apps.institutions.data_displays.urls')),
)
