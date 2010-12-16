from django.conf.urls.defaults import *
from django.views.decorators.cache import never_cache
from django.views.generic.simple import direct_to_template

from stars.apps.institutions.views import *
from stars.apps.credits.models import CreditSet
from stars.apps.helpers.forms.views import TemplateView

creditset = CreditSet.objects.get(pk=2)

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

urlpatterns += patterns(
    'django.views.generic.simple',
    # data views
    (r'^data-views/$', "direct_to_template",{'template': 'institutions/data_views/index.html'}),
    (r'^data-views/score/$', "direct_to_template",
                                    {'template': 'institutions/data_views/score.html',
                                     'extra_context': {'creditset': creditset}}),
    (r'^data-views/content/$', "direct_to_template",
                                    {'template': 'institutions/data_views/content.html',
                                     'extra_context': {'creditset': creditset}}),
    (r'^data-views/stats/$', "direct_to_template",
                                    {'template': 'institutions/data_views/statistics.html',
                                     'extra_context': {'creditset': creditset}}),
    (r'^data-views/dashboard/$', "direct_to_template", {'template': 'institutions/data_views/dashboard.html'}),
)