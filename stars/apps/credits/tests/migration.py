"""
    Test for migrating a creditset
"""

from django.test import TestCase

from stars.apps.credits.models import *
from stars.apps.credits.utils import migrate_set
from stars.apps.submissions.models import CreditTestSubmission

import sys
from datetime import date

class TestMigration(TestCase):
    
    fixtures = ['credits_testdata.json', 'credits_testcases.json']
    
    def setUp(self):
        pass
    
    def testCopyCreditSet(self):
        print >> sys.stderr, "Test: copy creditset"
        cs = CreditSet.objects.get(pk=2)
        new_cs = migrate_set(cs, "1.1", date.today())
        
        print "Categories: %d" % new_cs.category_set.count()
        self.assertEqual(new_cs.category_set.count(), cs.category_set.count())
        
        print "Subcategories: %d" % Subcategory.objects.filter(category__creditset=new_cs).count()
        self.assertEqual(Subcategory.objects.filter(category__creditset=new_cs).count(), Subcategory.objects.filter(category__creditset=cs).count())
        
        print "Credits: %d" % Credit.objects.filter(subcategory__category__creditset=new_cs).count()
        self.assertEqual(Credit.objects.filter(subcategory__category__creditset=new_cs).count(), Credit.objects.filter(subcategory__category__creditset=cs).count())
        
        print "Applicability Reasons: %d" % ApplicabilityReason.objects.filter(credit__subcategory__category__creditset=new_cs).count()
        self.assertEqual(ApplicabilityReason.objects.filter(credit__subcategory__category__creditset=new_cs).count(), ApplicabilityReason.objects.filter(credit__subcategory__category__creditset=cs).count())
        
        print "Documentation Fields: %d" % DocumentationField.objects.filter(credit__subcategory__category__creditset=new_cs).count()
        self.assertEqual(DocumentationField.objects.filter(credit__subcategory__category__creditset=new_cs).count(), DocumentationField.objects.filter(credit__subcategory__category__creditset=cs).count())
        
        print "Choices: %d" % Choice.objects.filter(documentation_field__credit__subcategory__category__creditset=new_cs).count()
        self.assertEqual(Choice.objects.filter(documentation_field__credit__subcategory__category__creditset=new_cs).count(), Choice.objects.filter(documentation_field__credit__subcategory__category__creditset=cs).count())
        
        print "CreditTestSubmissions: %d" % CreditTestSubmission.objects.filter(credit__subcategory__category__creditset=new_cs).count()
        self.assertEqual(CreditTestSubmission.objects.filter(credit__subcategory__category__creditset=new_cs).count(), CreditTestSubmission.objects.filter(credit__subcategory__category__creditset=cs).count())
        
        