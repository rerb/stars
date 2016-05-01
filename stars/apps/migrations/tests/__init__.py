from creditset_migration_tests import CreditSetMigrationTest
from submission_migration_tests import (VersionMigrationTest,
                                        VersionMigrationLiveServerTest,
                                        DataMigrationLiveServerTest)


__test__ = {test.__name__: test for test in [CreditSetMigrationTest,
                                             VersionMigrationTest,
                                             VersionMigrationLiveServerTest,
                                             DataMigrationLiveServerTest]}
