"""
    Test for migrating a creditset
"""

from django.test import TestCase

from stars.apps.credits.models import CreditSet, IncrementalFeature

import sys
from datetime import date

class TestIncrementalFeatures(TestCase):
    
    fixtures = ['credits_incremental_feature_test.json']
    
    def setUp(self):
        pass
    
    def testGetAttribute(self):
        print >> sys.stderr, "Test Incremental Features"
        cs = CreditSet.objects.get(pk=1)
        self.assertFalse(cs.is_locked)
        
        self.assertTrue(cs.has_feature_one_feature)
        self.assertFalse(cs.has_feature_two_feature)
        