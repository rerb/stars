from creditset_migration_tests import TestMigration
from submission_migration_tests import (VersionMigrationTest,
                                        VersionMigrationLiveServerTest,
                                        DataMigrationLiveServerTest)


__test__ = { test.__name__: test for test in [TestMigration,
                                              VersionMigrationTest,
                                              VersionMigrationLiveServerTest,
                                              DataMigrationLiveServerTest]
         }
