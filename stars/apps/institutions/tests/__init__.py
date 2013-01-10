from stars.apps.institutions.api.test import InstitutionResourceTestCase
from stars.apps.institutions.tests import stars_account, permissions, \
     pending_accounts, test_tags
from stars.apps.institutions.tests.institution import InstitutionTest
from stars.apps.institutions.tests.accuracy_inquiry import AccuracyInquiryTest
from stars.apps.institutions.tests.subscription import SubscriptionTest
from data_displays_views import AggregateFilterTest, ContentFilterTest, \
       ScoreFilterTest
from stars.apps.institutions.tests.views import SubmissionInquiryViewTest, \
    ActiveInstitutionsViewTest, RatedInstitutionsViewTest, ScorecardViewTest


__test__ = {
    'permissions': permissions,
    'stars_account': stars_account,
    'pending_accounts': pending_accounts,
    'test_tags': test_tags,
    'InstitutionTest': InstitutionTest,
    "AccuracyInquiryTest": AccuracyInquiryTest,
    'AggregateFilterTest': AggregateFilterTest,
    'ContentFilterTest': ContentFilterTest,
    'ScoreFilterTest': ScoreFilterTest,
    'SubmissionInquiryViewTest': SubmissionInquiryViewTest,
    'ActiveInstitutionsViewTest': ActiveInstitutionsViewTest,
    'RatedInstitutionsViewTest': RatedInstitutionsViewTest,
    'ScorecardViewTest': ScorecardViewTest,
    'SubscriptionTest': SubscriptionTest,
    'InstitutionResourceTestCase': InstitutionResourceTestCase,
}
