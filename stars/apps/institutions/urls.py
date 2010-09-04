from django.conf.urls.defaults import *
from stars.apps.institutions.views import *
from stars.apps.helpers.forms.views import TemplateView

urlpatterns = patterns(
    'stars.apps.institutions.views',
    
    # Active Institutions
    (r'^$', ActiveInstitutions(template="institutions/institution_list_active.html")),
    
    # All scorecards for an Institution
    (r'^(?P<institution_slug>[^/]+)/report/$', InstitutionScorecards(template='institutions/scorecards/list.html')),

    # Specific scorecard summary for an institution
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/$', ScorecardView(template='institutions/scorecards/summary.html')),
    
    # Category and Subcategory should redirect to summary
    # (r'^(?P<institution_slug>[^/]+)/scorecard/(?P<submissionset>[^/]+)/(?P<category_id>\d+)/$', ScorecardView(template='institutions/category_scorecard.html')),
    #  (r'^(?P<institution_slug>[^/]+)/scorecard/(?P<submissionset>[^/]+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/$', ScorecardView(template='institutions/subcategory_scorecard.html')),
    
    # Credit Scorecard
     (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/$', ScorecardView(template='institutions/scorecards/credit.html')),
    
    # Credit Documentation
     (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/documentation/$', ScorecardView(template='institutions/scorecards/credit_documentation.html')),
     
    # Internal Notes
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/internal-notes/$', ScorecardInternalNotesView(template='institutions/scorecards/internal_notes.html')),
)
