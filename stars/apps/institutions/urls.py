from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.institutions.views',
    
    (r'^$', 'institutions_active'),   # Once we have rated institutions, this should direct to the rated list.
    (r'^rated/$', 'institutions_rated'),
    (r'^active/$', 'institutions_active'),
    (r'^(?P<institution_id>\d+)/scorecard/$', 'scorecard', {'submissionset_id':None}),
    (r'^(?P<institution_id>\d+)/scorecard/(?P<submissionset_id>\d+)/$', 'scorecard'),
    (r'^(?P<institution_id>\d+)/scorecard/(?P<submissionset_id>\d+)/(?P<category_id>\d+)/$', 'category_scorecard'),
    (r'^(?P<institution_id>\d+)/scorecard/(?P<submissionset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/$', 'subcategory_scorecard'),
    (r'^(?P<institution_id>\d+)/scorecard/(?P<submissionset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/$', 'scorecard_credit_detail'),
)