"""
    Unittests for the submission renewal process
"""
from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.conf import settings

from datetime import date
import sys, os, random

from stars.apps.tool.manage.views import _gets_discount
from stars.apps.submissions.models import SubmissionSet

class RenewalTest(TestCase):
    fixtures = ['renewal_test_data.json']

    def setUp(self):
        pass
    
    def test_gets_discount(self):
        """
            current date: 3/1/11 (less than 90 days after 1/31/11)
                
                unsubmitted due before current_date
                unsubmitted due after current_date
                date submitted before current_date
                
            current date 5/1/11
            
                date submitted 30 days before current date
                date submitted 100 days before current date
                unsubmitted due 30 days before current date
                unsubmitted due 100 days before current date
                unsubmitted due after current date
                
            multiple submissions w/ different submission or due dates
        """
        
        ss = SubmissionSet.objects.get(pk=1)
        i = ss.institution
        
        current_date = date(year=2011, month=3, day=1)
        
        # unsubmitted due before current_date
        self.assertTrue(_gets_discount(i, current_date))
        # unsubmitted due after current_date
        ss.submission_deadline = date(year=2011, month=3, day=2)
        ss.save()
        self.assertFalse(_gets_discount(i, current_date))
        # date submitted before current_date
        ss.status = 'r'
        ss.date_submitted = date(year=2011, month=2, day=1)
        ss.save()
        self.assertTrue(_gets_discount(i, current_date))
        
        
        current_date = date(year=2012, month=5, day=1)
        
        # date submitted 30 days before current date
        ss.date_submitted = date(year=2012, month=4, day=1)
        ss.save()
        self.assertTrue(_gets_discount(i, current_date))
        
        # date submitted 100 days before current date
        ss.date_submitted = date(year=2012, month=1, day=1)
        ss.save()
        self.assertFalse(_gets_discount(i, current_date))
        
        # unsubmitted due 30 days before current date
        ss.status = 'ps'
        ss.date_submitted = None
        ss.submission_deadline = date(year=2012, month=4, day=1)
        ss.save()
        self.assertTrue(_gets_discount(i, current_date))
        
        # unsubmitted due 100 days before current date
        ss.submission_deadline = date(year=2012, month=1, day=1)
        ss.save()
        self.assertFalse(_gets_discount(i, current_date))
        
        # unsubmitted due after current date
        ss.submission_deadline = date(year=2012, month=6, day=1)
        ss.save()
        self.assertFalse(_gets_discount(i, current_date))