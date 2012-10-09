"""
    Test the credit structure mixin
"""

from django.test import TestCase
from django.http import Http404
from django.views.generic import TemplateView

from stars.apps.credits.views import CreditsetStructureMixin

import sys

class TestStructure(TestCase):
    fixtures = ['basic_creditset.json',]
    
    def setUp(self):
        pass
    
    def testMixin(self):
        """
        
        """
        class TestView(CreditsetStructureMixin, TemplateView):
            pass
        
        view = TestView()
        
        # /creditset_version/category_abbreviation/subcategory_slug/credit_number/field_id/
        kwargs = {}
        kwargs['creditset_version'] = "test"
        
        _context = view.get_context_data(**kwargs)
        cs = view.get_creditset()
        self.assertEqual(cs.id, 1)
        
        menu = view.get_creditset_nav()
        test_menu = [
                        {
                            'url': u'/test/TC/',
                            'selected': False,
                            'id': 1,
                            'title': u'Test Category',
                            'subcategories':
                                [
                                    {
                                        'tier2': [],
                                        'title': u'Test Subcategory',
                                        'url': u'/test/TC/test-subcategory/',
                                        'selected': False,
                                        'credits':
                                            [
                                                {
                                                    'url': u'/test/TC/test-subcategory/1/',
                                                    'selected': False,
                                                    'id': 1,
                                                    'title': u'ID?: Test Credit'
                                                }
                                             ],
                                        'id': 1
                                    }
                                 ]
                        }
                    ]
        self.assertEqual(menu, test_menu)
        
        # try a bogus category
        kwargs['category_abbreviation'] = 'TZ'
        
        try:
            _context = view.get_context_data(**kwargs)
        except Exception as e:
            self.assertEqual(e.__class__.__name__, "Http404")
        
        try:
            _context = view.get_context_data(**kwargs)
        except Exception as e:
            self.assertEqual(e.__class__.__name__, "Http404")
        
        # fix the category
        kwargs['category_abbreviation'] = 'TC'
        _context = view.get_context_data(**kwargs)
        cat = view.get_category()
        self.assertEqual(cat.id, 1)
        
        menu = view.get_creditset_nav()
        test_menu = [
                        {
                            'url': u'/test/TC/',
                            'selected': True,
                            'id': 1,
                            'title': u'Test Category',
                            'subcategories':
                                [
                                    {
                                        'tier2': [],
                                        'title': u'Test Subcategory',
                                        'url': u'/test/TC/test-subcategory/',
                                        'selected': False,
                                        'credits':
                                            [
                                                {
                                                    'url': u'/test/TC/test-subcategory/1/',
                                                    'selected': False,
                                                    'id': 1,
                                                    'title': u'ID?: Test Credit'
                                                }
                                             ],
                                        'id': 1
                                    }
                                 ]
                        }
                    ]
        self.assertEqual(menu, test_menu)
        
        kwargs['subcategory_slug'] = 'test-subcategory'
        kwargs['credit_number'] = 1
        kwargs['field_id'] = 1
        
        _context = view.get_context_data(**kwargs)
        