"""
    Test Suite for Credit system.  
    These tests cover all aspects of the credit system, including
     - the CreditSet hierarchy of models
     - the credit editor
     - credit editor template tags
"""
from django.test import TestCase
from stars.apps.credits.models import *

from stars.apps.tool.credit_editor.templatetags import ce_tags
class Credit_tags_Test(TestCase):
    fixtures = ['credits_testdata.json']
    
    """
        #######   ce_tags.py Test Suite.  #######
    """
    def test_show_field_form(self):
        set, cat, subcat, credit, field = self._get_test_credit_objects()

        tag_context = ce_tags.show_field_form(field)
        self.assertEqual(tag_context['documentation_field'].title, 'Total number of degree-seeking students enrolled at the institution')
        from stars.apps.tool.my_submission.forms import NumericSubmissionForm
        self.assertEqual(tag_context['field_form'].__class__, NumericSubmissionForm)


    def test_show_editor_crumbs(self):
        set, cat, subcat, credit, field  = self._get_test_credit_objects()

        tag_context = ce_tags.show_editor_crumbs(set)
        self.assertEqual(tag_context['object_set'], [set])

        tag_context = ce_tags.show_editor_crumbs(cat)
        self.assertEqual(tag_context['object_set'], [set, cat])

        tag_context = ce_tags.show_editor_crumbs(subcat)
        self.assertEqual(tag_context['object_set'], [set, cat, subcat])
    
        tag_context = ce_tags.show_editor_crumbs(credit)
        self.assertEqual(tag_context['object_set'], [set, cat, subcat, credit])

    def _get_test_credit_objects(self):
        """ Returns a known suite of test credit objects:
            credit set -> category -> subcategory -> credit -> documentation field
        """
        set = CreditSet.objects.get(id=2)
        self.assertEqual(set.version, u'1.0')

        cat = Category.objects.get(id=1)
        self.assertEqual(cat.title, u'Education & Research')        
 
        subcat = Subcategory.objects.get(id=1)
        self.assertEqual(subcat.title, u'Co-Curricular Education')
    
        credit = Credit.objects.get(id=1)
        self.assertEqual(credit.title, u'Student Sustainability Educators Program')

        field = DocumentationField.objects.get(id=2)
        self.assertEqual(field.title, u'Total number of degree-seeking students enrolled at the institution')

        return set, cat, subcat, credit, field
