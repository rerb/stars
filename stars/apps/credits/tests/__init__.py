from incremental_features import TestIncrementalFeatures
from utils import TestUtils
from stars.apps.credits.api.test import CategoryResourceTestCase, \
     CreditSetResourceTestCase, SubcategoryResourceTestCase, \
     CreditResourceTestCase, DocumentationFieldResourceTestCase
from credit import CreditTest
from creditset import CreditsetTest
from views import TestStructure

__test__ = {
    'TestIncrementalFeatures': TestIncrementalFeatures,
    'TestUtils': TestUtils,
    'CreditSetResourceTestCase': CreditSetResourceTestCase,
    'CategoryResourceTestCase': CategoryResourceTestCase,
    'SubcategoryResourceTestCase': SubcategoryResourceTestCase,
    'CreditResourceTestCase': CreditResourceTestCase,
    'DocumentationFieldResourceTestCase': DocumentationFieldResourceTestCase,
    'CreditTest': CreditTest,
    'CreditsetTest': CreditsetTest,
    'TestStructure': TestStructure,
    }
