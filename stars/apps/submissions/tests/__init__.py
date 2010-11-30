from stars.apps.submissions.tests import scoring
from submission_manager import ManagerTest
from extensions import ExtensionTest

__test__ = {
    'manager': ManagerTest,
    'scoring': scoring,
    'extensions': ExtensionTest,
}
