from django.conf.urls.defaults import *

urlpatterns = patterns(
    'stars.apps.dashboard.submissions.views',
    
    (r'^$', 'summary'),
    (r'^add-responsible-party/$', 'add_responsible_party'),
    (r'^(?P<category_id>\d+)/$', 'category_detail'),
    (r'^(?P<category_id>\d+)/(?P<subcategory_id>\d+)/$', 'subcategory_detail'),
    (r'^(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/$', 'credit_detail'),
)