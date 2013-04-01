"""
    Test the credit structure mixin
"""

from django.test import TestCase
from django.http import Http404
from django.views.generic import TemplateView

from stars.apps.submissions.views import SubmissionStructureMixin
from stars.apps.submissions.models import CreditUserSubmission, CreditSubmission

import sys

class TestSubmissionStructureMixin(TestCase):
    fixtures = ['institutions_testdata.json', 'basic_creditset.json', 'basic_submissionset.json']
    
    def setUp(self):
        pass
    
    def testMixin(self):
        """
        
        """
        class TestView(SubmissionStructureMixin, TemplateView):
            pass
        
        view = TestView()
        
        """
            /institution_slug/submissionset_date/category_abbreviation/subcategory_slug/credit_number/
            or
            /institution_slug/submissionset_id/category_abbreviation/subcategory_slug/credit_number/
        """
        kwargs = {}
        kwargs['institution_slug'] = "test-institution"
        kwargs['submissionset_id'] = 1
        
        _context = view.get_context_data(**kwargs)
        
        ss = view.get_submissionset()
        self.assertEqual(ss.id, 1)
        
        cs = view.get_creditset()
        self.assertEqual(cs.id, 1)
        
        
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
        cat = view.get_categorysubmission()
        self.assertEqual(cat.id, 1)
        
        kwargs['subcategory_slug'] = 'test-subcategory'
        kwargs['credit_number'] = 1
        
        _context = view.get_context_data(**kwargs)
        
        sub = view.get_subcategorysubmission()
        self.assertEqual(sub.id, 1)
        
        credit = view.get_creditusersubmission()
        self.assertEqual(credit.id, 1)