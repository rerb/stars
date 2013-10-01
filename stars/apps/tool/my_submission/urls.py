from django.conf.urls.defaults import patterns, url

from stars.apps.helpers.forms.forms import Confirm
from stars.apps.tool.my_submission.forms import (ExecContactForm,
                                                 LetterForm,
                                                 StatusForm)
from stars.apps.tool.my_submission.views import (
    AddResponsiblePartyView,
    CreditDocumentationView,
    CreditHistoryView,
    CreditNotesView,
    CreditSubmissionDetailView,
    EditBoundaryView,
    RatingCongratulationsView,
    SaveSnapshot,
    SubcagegorySubmissionDetailView,
    SubmissionSummaryView,
    SubmitForRatingWizard)


from django.views.decorators.cache import never_cache

from stars.apps.institutions.views import PDFDownloadView, ExcelDownloadView

SUBCAT_PATH = "(?P<category_abbreviation>[\w-]+)/(?P<subcategory_slug>[\w-]+)"
CREDIT_PATH = "%s%s" % (SUBCAT_PATH, "/(?P<credit_identifier>[\w-]+)")

urlpatterns = patterns(
    '',

    url(r'^$', SubmissionSummaryView.as_view(),
        name='submission-summary'),

    # Export retrieval view
    url(r'^pdf/download/(?P<task>[^/]+)/$',
     never_cache(PDFDownloadView.as_view())),

    # Export retrieval view
    url(r'^excel/download/(?P<task>[^/]+)/$',
     never_cache(ExcelDownloadView.as_view())),

    # Submit a snaphot
    url(r'^snapshot/$', SaveSnapshot.as_view(), name='save-snapshot'),

    # Submit for rating
    url(r'^submit/$',
        SubmitForRatingWizard.as_view([StatusForm,
                                       LetterForm,
                                       ExecContactForm,
                                       Confirm]),
        name='submission-submit'),

    url(r'^submit/success/$', RatingCongratulationsView.as_view(),
        name='submit-success'),

    url(r'^boundary/$', EditBoundaryView.as_view(),
        name='boundary-edit'),

    url(r'^add-responsible-party/$', AddResponsiblePartyView.as_view(),
        name='add-responsible-party'),

    url(r'^%s/$' % SUBCAT_PATH,
     SubcagegorySubmissionDetailView.as_view(),
     name='subcategory-submit'),

    url(r'^%s/$' % CREDIT_PATH,
        CreditSubmissionDetailView.as_view(),
        name='creditsubmission-submit'),

    url(r'^%s/documentation/$' % CREDIT_PATH,
        CreditDocumentationView.as_view(),
        name='creditdocs-submit'),

    url(r'^%s/notes/$' % CREDIT_PATH,
        CreditNotesView.as_view(),
        name='creditnotes-submit'),

    url(r'^%s/history/$' % CREDIT_PATH,
        CreditHistoryView.as_view(),
        name='credit-history')
)
