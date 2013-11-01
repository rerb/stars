"""
    Test for migrating a creditset
"""

from django.test import TestCase

from stars.apps.credits.models import *
from stars.apps.migrations.utils import migrate_creditset
from stars.apps.submissions.models import CreditTestSubmission

import sys
from datetime import date

class TestMigration(TestCase):
    
    fixtures = ['credits_testdata.json', 'credits_testcases.json']
    
    def setUp(self):
        pass
    
    def testGetLatest(self):
        cs = CreditSet.objects.get_latest()
        self.assertEqual(cs.id, 2)
        
    
    def testCopyCreditSet(self):
        cs = CreditSet.objects.get(pk=2)
        new_cs = migrate_creditset(cs, "1.1", date.today())
        
        self.assertEqual(new_cs.category_set.count(), cs.category_set.count())
        
        self.assertEqual(
            Subcategory.objects.filter(category__creditset=new_cs).count(),
            Subcategory.objects.filter(category__creditset=cs).count())
        
        self.assertEqual(
            Credit.objects.filter(
                subcategory__category__creditset=new_cs).count(),
            Credit.objects.filter(
                subcategory__category__creditset=cs).count())
        
        self.assertEqual(
            ApplicabilityReason.objects.filter(
                credit__subcategory__category__creditset=new_cs).count(),
            ApplicabilityReason.objects.filter(
                credit__subcategory__category__creditset=cs).count())
        
        self.assertEqual(
            DocumentationField.objects.filter(
                credit__subcategory__category__creditset=new_cs).count(),
            DocumentationField.objects.filter(
                credit__subcategory__category__creditset=cs).count())
        
        self.assertEqual(
            Choice.objects.filter(
                documentation_field__credit__subcategory__category__creditset=new_cs).count(),
            Choice.objects.filter(
                documentation_field__credit__subcategory__category__creditset=cs).count())
        
        self.assertEqual(
            CreditTestSubmission.objects.filter(
                credit__subcategory__category__creditset=new_cs).count(),
            CreditTestSubmission.objects.filter(
                credit__subcategory__category__creditset=cs).count())
        
        
