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
from django.conf import settings

from stars.apps.registration.views import process_payment

from datetime import date
import sys, os, random

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
    
    def testPayment(self):
        
        login = settings.TEST_AUTHORIZENET_LOGIN
        key = settings.TEST_AUTHORIZENET_KEY
        server = settings.TEST_AUTHORIZENET_SERVER
        
        # Test payment
        invoice = random.random()
        today = date.today()
        payment_dict = {
                            'cc_number': '4007000000027',
                            'exp_date': "%d%d" % (today.month, (today.year+1)),
                            'cv_number': '123',
                            'billing_address': '123 Street Rd',
                            'billing_address_line_2': '',
                            'billing_city': 'City',
                            'billing_state': 'ST',
                            'billing_zipcode': '12345',
                            'country': "USA",
                            'billing_firstname': "first name",
                            'billing_lastname': 'last name',
                            'description': "%s STARS Registration" % "BOGUS INSTITUTION",
                        }
        product_list = [{'name': 'test', 'price': 1, 'quantity': 1},]
        response = process_payment(
                                   payment_dict,
                                   product_list,
                                   invoice_num=invoice,
                                   server=server,
                                   login=login,
                                   key=key
                                   )
        print >> sys.stderr, response
        self.assertTrue(response['cleared'] == True)
        self.assertTrue(response['trans_id'] != None)
        
        # Test duplicate transactions
        response = process_payment(
                                   payment_dict,
                                   product_list,
                                   invoice_num=invoice,
                                   server=server,
                                   login=login,
                                   key=key
                                   )
        print >> sys.stderr, response
        self.assertTrue(response['cleared'] == False)
        self.assertTrue(response['msg'] == 'A duplicate transaction has been submitted.')
        
        # multiple products
        product_list = [{'name': 'test', 'price': 1, 'quantity': 2},]
        response = process_payment(payment_dict,
                                   product_list,
                                   invoice_num=invoice,
                                   server=server,
                                   login=login,
                                   key=key
                                   )
        print >> sys.stderr, response
        self.assertTrue(response['cleared'] == True)
        self.assertTrue(response['trans_id'] != None)
        
        