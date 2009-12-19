"""
    Test Suite for Credit system.  
    These tests cover all aspects of the credit system, including
     - the CreditSet hierarchy of models
     - the credit editor
     - credit editor template tags
"""
from django.test import TestCase
from stars.apps.credits.models import *

from apps.tool.credit_editor.templatetags import ce_tags
class Credit_tags_Test(TestCase):
    fixtures = ['v0.5-categories.json', 'v0.5-credits.json']
    
    """
        #######   ce_tags.py Test Suite.  #######
    """
    def test_show_field_form(self):
        set, cat, subcat, credit, field = self._get_test_credit_objects()

        tag_context = ce_tags.show_field_form(field)
        self.assertEqual(tag_context['documentation_field'].title, 'Website URL where the green building policy is posted')
        from stars.apps.tool.submissions.forms import URLSubmissionForm
        self.assertEqual(tag_context['field_form'].__class__, URLSubmissionForm)


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
        set = CreditSet.objects.all()[0]
        self.assertEqual(set.version, u'0.5')

        cat = Category.objects.all()[1]
        self.assertEqual(cat.title, u'Operations')        
 
        subcat = Subcategory.objects.all()[4]
        self.assertEqual(subcat.title, u'Buildings')
    
        credit = Credit.objects.all()[0]
        self.assertEqual(credit.title, u'New Green Buildings')

        field = DocumentationField.objects.all()[0]
        self.assertEqual(field.title, u'Website URL where the green building policy is posted')

        return set, cat, subcat, credit, field
