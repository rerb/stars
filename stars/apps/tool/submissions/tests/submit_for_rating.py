"""
    Doctests for the submit for rating tool that will process an institutions
    submission and notify the liason and STARS Staff

    Test premises:
        - the forms are processed correctly
            - Confirmation form
            - Letter Submission
            - Finalize
        - email notifications are sent
"""
from django.test import TestCase
from django.core import mail
from django.test.client import Client

from stars.apps.submissions.models import SubmissionSet

from datetime import date
import sys, os

class RatingTest(TestCase):
    fixtures = ['submit_for_rating_tests.json',]

    def setUp(self):
        pass
        
    def testConfirmView(self):
        """
            Test the ConfirmClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and returns a redirect to step 2
        """
        c = Client()
        c.login(username='test_user', password='test')
        post_dict = {}
        response = c.get('/tool/submissions/submit/', post_dict)
        self.assertTrue(response.status_code == 200)
        
        post_dict = {'submission_boundary': 'boundary text',}
        response = c.post('/tool/submissions/submit/', post_dict, follow=False)
        self.assertTrue(response.status_code == 302)
        
    def testLetterView(self):
        """
            Tests the LetterClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and redirects to step 3
        """
        
        c = Client()
        c.login(username='test_user', password='test')
        post_dict = {}
        response = c.get('/tool/submissions/submit/letter/', post_dict)
        self.assertTrue(response.status_code == 200)
        
        f = open(os.path.join(os.path.dirname(__file__), 'test.pdf'))
        
        post_dict = {'presidents_letter': f,}
        response = c.post('/tool/submissions/submit/letter/', post_dict, follow=False)
        self.assertTrue(response.status_code == 302)

    def testFinalizeView(self):
        """
            Tests the LetterClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and saves the SubmissionSet object
                - Sends emails to liason, user and stars staff
        """
        
        c = Client()
        c.login(username='test_user', password='test')
        post_dict = {}
        response = c.get('/tool/submissions/submit/finalize/', post_dict)
        self.assertTrue(response.status_code == 200)
        
        post_dict = {'confirm': 1,}
        response = c.post('/tool/submissions/submit/finalize/', post_dict, follow=False)
        self.assertTrue(response.status_code == 200)
        ss = SubmissionSet.objects.get(pk=1)
        self.assertTrue(ss.status == 'pr')
        self.assertTrue(len(mail.outbox) == 2)
        