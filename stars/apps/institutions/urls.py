from django.conf.urls.defaults import *
from stars.apps.institutions.views import *
from stars.apps.helpers.forms.views import TemplateView

urlpatterns = patterns(
    'stars.apps.institutions.views',
    
    # This uses class-based views.
    (r'^$', ActiveInstitutions(template="institutions/institution_list_active.html")),
    
    (r'^(?P<category_id>\d+)/(?P<subcategory>\d+)/$', CreditBrowsingView(template="institutions/institution_list_active.html")),
    
    # (r'^(?P<institution_id>\d+)/scorecard/$', 'scorecard', {'submissionset_id':None}),
    
    (r'^(?P<institution_id>\d+)/scorecard/(?P<submissionset_id>\d+)/$', ScorecardView(template='institutions/scorecards/summary.html')),
    
    # (r'^(?P<institution_id>\d+)/scorecard/(?P<submissionset_id>\d+)/(?P<category_id>\d+)/$', ScorecardView(template='institutions/category_scorecard.html')),
    #  (r'^(?P<institution_id>\d+)/scorecard/(?P<submissionset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/$', ScorecardView(template='institutions/subcategory_scorecard.html')),
     (r'^(?P<institution_id>\d+)/scorecard/(?P<submissionset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/$', ScorecardView(template='institutions/scorecards/credit.html')),
     (r'^(?P<institution_id>\d+)/scorecard/(?P<submissionset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/documentation/$', ScorecardView(template='institutions/scorecards/credit_documentation.html')),
)