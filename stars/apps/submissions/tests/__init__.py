from stars.apps.submissions.tests import scoring
from submission_manager import ManagerTest
from extensions import ExtensionTest
from submission_migration_tests import MigrationTest
#from pdf import PDFTest

__test__ = {
    'manager': ManagerTest,
    'scoring': scoring,
    'extensions': ExtensionTest,
    'migrations': MigrationTest,
#    'pdf': PDFTest,
}
