from incremental_features import TestIncrementalFeatures
from utils import TestUtils
from stars.apps.credits.api.test import (CategoryResourceTestCase,
                                         CreditResourceTestCase,
                                         CreditSetResourceTestCase,
                                         DocumentationFieldResourceTestCase,
                                         SubcategoryResourceTestCase)

from credit import CreditTest
from creditset import CreditSetTest
from documentation_field import DocumentationFieldTestCase
from unit import UnitTest  # :-)
from views import TestStructure

__test__ = {
    'TestIncrementalFeatures': TestIncrementalFeatures,
    'TestUtils': TestUtils,
    'CreditSetResourceTestCase': CreditSetResourceTestCase,
    'CategoryResourceTestCase': CategoryResourceTestCase,
    'DocumentationFieldTestCase': DocumentationFieldTestCase,
    'SubcategoryResourceTestCase': SubcategoryResourceTestCase,
    'CreditResourceTestCase': CreditResourceTestCase,
    'DocumentationFieldResourceTestCase': DocumentationFieldResourceTestCase,
    'CreditTest': CreditTest,
    'CreditSetTest': CreditSetTest,
    'TestStructure': TestStructure,
    'UnitTest': UnitTest
}
