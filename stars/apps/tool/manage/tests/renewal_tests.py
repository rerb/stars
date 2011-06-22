"""
    Unittests for the submission renewal process
"""
from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.conf import settings
from django.contrib.auth.models import User

from datetime import date
import sys, os, random

from stars.apps.tool.manage.views import _gets_discount
from stars.apps.submissions.models import SubmissionSet, NumericSubmission

class RenewalTest(TestCase):
    fixtures = ['submission_migration_test.json', 'notification_emailtemplate_tests.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
    
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
        
        current_date = date(year=2011, month=5, day=14)
        self.assertTrue(_gets_discount(i, current_date))
        
        current_date = date(year=2011, month=5, day=16)
        self.assertFalse(_gets_discount(i, current_date))
        
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
        
    def test_purchase_submission(self):
        """
            purchase_submissionset()
            
            Page loads
            - 200 response code
            
            Pay Later
            - results in a new submission
            - sends an email
            
            Pay w/ CC
            - transaction processes
            - results in a new submission
            - sends an email
        """
        
        user = User.objects.get(pk=1)
        user.set_password('test')
        user.save()
        
        c = Client()
        login = c.login(username='tester', password='test')
        self.assertTrue(login)
        
        # Total Submissions
        self.assertEqual(SubmissionSet.objects.count(), 1)
        
        url = "/tool/manage/submissionsets/purchase/"
        
        # Page Loads
        response = c.get(url)
        self.assertTrue(response.status_code == 200)
        
        # Pay Later
        post_dict = {'confirm': u'on',}
        response = c.post(url, post_dict)
        self.assertTrue(response.status_code == 302)
        
        self.assertEqual(SubmissionSet.objects.count(), 2)
        self.assertTrue(len(mail.outbox) == 2)
        
        # confirm the data migration
        self.assertEqual(NumericSubmission.objects.count(), 2)
        ns1 = NumericSubmission.objects.all()[0]
        ns2 = NumericSubmission.objects.all()[1]
        self.assertEqual(ns1.value, ns2.value)
        
       # print >> sys.stdout, mail.outbox[1].message()
        
        # # Pay Now
        # post_dict = {
        #                'name_on_card': 'Test Person',
        #                'card_number': '4007000000027',
        #                # 'card_number': '4222222222222',
        #                'exp_month': str(date.today().month),
        #                'exp_year': str(date.today().year + 1),
        #                'cv_code': '123',
        #                'billing_address': '123 Street rd',
        #                'billing_city': "City",
        #                'billing_state': 'RI',
        #                'billing_zipcode': '01234',
        #             }
        # response = c.post(url, post_dict)
        # self.assertTrue(response.status_code == 302)
        # 
        # self.assertTrue(SubmissionSet.objects.count() == 3)
        # self.assertTrue(len(mail.outbox) == 4)
        