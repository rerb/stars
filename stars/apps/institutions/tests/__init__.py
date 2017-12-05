from stars.apps.institutions.api.test import InstitutionResourceTestCase
from stars.apps.institutions.tests import (stars_account, permissions,
                                           pending_accounts, test_tags)
from stars.apps.institutions.tests.institution import InstitutionTest
from stars.apps.institutions.tests.accuracy_inquiry import AccuracyInquiryTest
from stars.apps.institutions.tests.subscription import SubscriptionTest
from stars.apps.institutions.tests.views import (RatedInstitutionsViewTest,
                                                 ScorecardViewTest,
                                                 TopLevelTest)


__test__ = {
    'permissions': permissions,
    'stars_account': stars_account,
    'pending_accounts': pending_accounts,
    'test_tags': test_tags,
    'InstitutionTest': InstitutionTest,
    "AccuracyInquiryTest": AccuracyInquiryTest,
    'RatedInstitutionsViewTest': RatedInstitutionsViewTest,
    'ScorecardViewTest': ScorecardViewTest,
    'SubscriptionTest': SubscriptionTest,
    'TopLevelTest': TopLevelTest,
    'InstitutionResourceTestCase': InstitutionResourceTestCase
}
