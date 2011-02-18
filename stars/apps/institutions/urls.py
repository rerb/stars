from django.conf.urls.defaults import *
from stars.apps.institutions.views import *
from stars.apps.helpers.forms.views import TemplateView
from django.views.decorators.cache import never_cache

urlpatterns = patterns(
    'stars.apps.institutions.views',
    
    # Active Institutions
    (r'^$', ActiveInstitutions(template="institutions/institution_list_active.html")),
    
    # Submission Inquiry Form
    (r'^inquiry/$', 'inquiry_select_institution'),
    
    # All scorecards for an Institution
    (r'^(?P<institution_slug>[^/]+)/report/$', InstitutionScorecards(template='institutions/scorecards/list.html')),

    # Specific scorecard summary for an institution
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/$', ScorecardView(template='institutions/scorecards/summary.html')),
    
    # Specific scorecard summary for an institution
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/inquiry/$', SubmissionInquiryView()),
    
    # PDF Export of Submission
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/pdf/$', never_cache(PDFExportView(template=None))),

    # Credit Scorecard
     (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/$', ScorecardView(template='institutions/scorecards/credit.html')),
    
    # Data correction request
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/(?P<field_type>\d+)/(?P<field_id>\d+)/$', data_correction_view),
    
    # Credit Documentation
     (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/documentation/$', ScorecardView(template='institutions/scorecards/credit_documentation.html')),
     
    # Internal Notes
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/internal-notes/$', ScorecardInternalNotesView(template='institutions/scorecards/internal_notes.html')),
)
