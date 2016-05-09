from creditset_migration_tests import CreditSetMigrationTest
from submission_migration_tests import (VersionMigrationTest,
                                        MigrateSubmissionTestCase)


__test__ = {test.__name__: test for test in [CreditSetMigrationTest,
                                             VersionMigrationTest,
                                             MigrateSubmissionTestCase]}
