from stars.apps.institutions.api.test import InstitutionResourceTestCase
from stars.apps.institutions.tests import stars_account, permissions, \
     pending_accounts, test_tags
from stars.apps.institutions.tests.institution import InstitutionTest

__test__ = {
    'permissions': permissions,
    'stars_account': stars_account,
    'pending_accounts': pending_accounts,
    'test_tags': test_tags,
    'InstitutionTest': InstitutionTest
}
