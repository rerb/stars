from django.conf.urls.defaults import patterns, url
from stars.apps.tool.my_submission.views import (ConfirmClassView,
                                                 EditBoundaryView,
                                                 SaveSnapshot,
                                                 SubmissionSummaryView)

urlpatterns = patterns(
    'stars.apps.tool.my_submission.views',

    url(r'^$', SubmissionSummaryView.as_view(),
        name='submission-summary'),

    url(r'^boundary/$', EditBoundaryView.as_view(),
        name='boundary-edit'),

    (r'^add-responsible-party/$', 'add_responsible_party'),
    (r'^(?P<category_id>\d+)/(?P<subcategory_id>\d+)/$', 'subcategory_detail'),

    url(r'^(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/$',
        'credit_detail',
        name='creditsubmission-submit'),

    (r'^(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/documentation/$', 'credit_documentation'),
    (r'^(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/notes/$', 'credit_notes'),
    # uploaded file access
    (r'^my_uploads/secure/(?P<inst_id>\d+)/(?P<path>.+)$', 'serve_uploaded_file'),

    # Submit for Rating
    #(r'^submit/$', 'submit_for_rating'),
    url(r'^snapshot/$', SaveSnapshot.as_view(), name='save-snapshot'),

    url(r'^submit/$', ConfirmClassView.as_view(),
        name='submission-submit'),

    # (r'^submit/status/', 'submit_status'),

    ######################################################################
    # TODO: Commenting out submit_letter and submit_finalize temporarily #
    # since their definitions in .../views.py are temporarily            #
    # unavailable because of a bug in RulesMixin (see comments in        #
    # .../views.py for details):                                         #
    ######################################################################
    # (r'^submit/letter/$', 'submit_letter'),
    # (r'^submit/finalize/$', 'submit_finalize'),
    (r'^gateway/media/secure/(?P<inst_id>\d+)/(?P<creditset_id>\d+)/(?P<credit_id>\d+)/(?P<field_id>\d+)/(?P<filename>[^/]+)/delete/$', 'delete_uploaded_file_gateway'),
)
