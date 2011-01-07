"""
    Doctests for the registration process

    Test premises:
        - the forms are processed correctly
            - Select Institution Form
            - Contact Form
            - Payment Form
        - email notifications are sent
"""
from django.test import TestCase
from django.core import mail
from django.test.client import Client

from datetime import date
import sys, os

class TestProcess(TestCase):
    fixtures = ['registration_tests.json']

    def setUp(self):
        pass
        
    def testViews(self):
        """
            Test the ConfirmClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and returns a redirect to step 2
        """
        
        # Select Institution
        
        url = '/register/' 
        
        c = Client()
        c.login(username='test_user', password='test')
        post_dict = {}
        response = c.get(url, post_dict)
        self.assertTrue(response.status_code == 200)
        
        post_dict = {'aashe_id': '24394',}
        response = c.post(url, post_dict, follow=False)
        self.assertTrue(response.status_code == 302)
        
        self.assertTrue(c.session['selected_institution'].slug == 'okanagan-college-british-columbia')
        
        # Contact Information
        
        url = '/register/step2/'
        
        # Empty Query
        post_dict = {}
        response = c.get(url, post_dict)
        self.assertTrue(response.status_code == 200)
        
        
        # Same Emails
        post_dict = {
                     "contact_first_name": 'test',
                     'contact_last_name': 'test',
                     'contact_title': 'test',
                     'contact_department': 'test',
                     'contact_phone': '123 555 1212',
                     'contact_email': 'test@aashe.org',
                     
                     "executive_contact_first_name": 'test',
                     'executive_contact_last_name': 'test',
                     'executive_contact_title': 'test',
                     'executive_contact_department': 'test',
                     'executive_contact_email': 'test@aashe.org',
                    }
        response = c.get(url, post_dict)
        self.assertTrue(response.status_code == 200)
        
        post_dict['contact_email'] = 'test2@aashe.org'
        response = c.post(url, post_dict, follow=False)
        self.assertTrue(response.status_code == 302)
        
        self.assertTrue(c.session['selected_institution'].slug == 'okanagan-college-british-columbia')
        
        # Test Payment
        url = '/register/step3/'
        
        # Empty Query
        post_dict = {}
        response = c.get(url, post_dict)
        self.assertTrue(response.status_code == 200)
        
        # Pay Later
        post_dict = {'confirm': u'on',}
        response = c.post(url, post_dict)
        self.assertTrue(response.status_code == 302)
        
        #@Todo Test payment