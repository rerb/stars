from django.conf.urls.defaults import *
from django.views.decorators.cache import never_cache, cache_page
## Caching of views set as (86400 * number of days)

from stars.apps.institutions.views import *

urlpatterns = patterns(
    'stars.apps.institutions.views',

    # Active Institutions
    (r'^$', ActiveInstitutions.as_view()),

    # Rated institutions
    (r'^rated/$', RatedInstitutions.as_view()),

    # Rated institutions
    url(r'^participants-and-reports/$', ParticipantReportsView.as_view(),
        name='participants-reports'),

    # Submission Inquiry Form
    url(r'^inquiry/$', SubmissionInquirySelectView.as_view(),
        name='submission-inquiry'),

    # All scorecards for an Institution
    url(r'^(?P<institution_slug>[^/]+)/report/$',
        cache_page(86400 * 1, cache="filecache")(InstitutionScorecards.as_view()), name='scorecard-list'),

    # Specific scorecard summary for an institution
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/$',
        cache_page(86400 * 1, cache="filecache")(ScorecardSummary.as_view()), name='scorecard-summary'),

    # Submission inquiry for an institution
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/inquiry/$',
        SubmissionInquiryView.as_view(),
        name='institution-submission-inquiry'),

    #
    # Exports
    #

    # PDF Export of Submission
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/pdf/$',
     never_cache(PDFExportView.as_view())),

    # PDF retrieval view
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/pdf/download/(?P<task>[^/]+)/$',
     never_cache(PDFDownloadView.as_view())),

    # Excel Export of Submission
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/excel/$',
     never_cache(ExcelExportView.as_view())),

    # Export retrieval view
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/excel/download/(?P<task>[^/]+)/$',
     never_cache(ExcelDownloadView.as_view())),

    # Certificate Export of Submission
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/cert/$',
        never_cache(CertificateExportView.as_view()),
        name="cert-export"),

    # Certificate retrieval view
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/cert/download/(?P<task>[^/]+)/$',
        never_cache(CertificateDownloadView.as_view()),
        name="cert-download"
    ),

    # Certificate preview
    url(r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/cert-preview/$',
        never_cache(ScorecardCertPreview.as_view()),
        name="cert-preview"),

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
