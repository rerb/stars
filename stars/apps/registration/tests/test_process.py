"""
    Unittests for the registration process

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
from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import Institution, SubscriptionPayment

from aashe.issdjango.models import Organizations

from datetime import date
import sys, os, random

class TestProcess(TestCase):
    fixtures = ['registration_tests.json', 'iss_testdata.json', 'notification_emailtemplate_tests.json']
    multi_db = True

    def setUp(self):
        pass
        
    def regInternational(self, name, slug):
        """
            Run the first step for international registration
        """
        url = '/register/international/' 

        c = Client()
        c.login(username='test_user', password='test')
        post_dict = {}
        response = c.get(url, post_dict)
        self.assertTrue(response.status_code == 200)

        post_dict = {'institution_name': name,}
        response = c.post(url, post_dict, follow=False)
        self.assertTrue(response.status_code == 302)

        self.assertTrue(c.session['selected_institution'].slug == slug)
        self.assertTrue(c.session['selected_institution'].international)
        
        return c
        
    def regStep1(self, id, slug):
        """
            Run the first step of registration
        """
        
        # Select Institution

        url = '/register/' 

        c = Client()
        c.login(username='test_user', password='test')
        post_dict = {}
        response = c.get(url, post_dict)
        self.assertTrue(response.status_code == 200)

        post_dict = {'aashe_id': id,}
        response = c.post(url, post_dict, follow=False)
        self.assertTrue(response.status_code == 302)

        self.assertTrue(c.session['selected_institution'].slug == slug)
        
        return c
    
    def regStep2_participant(self, c, slug):
        
        url = '/register/step2/'

        post_dict = {}
        response = c.get(url, post_dict)
        self.assertTrue(response.status_code == 200)

        post_dict = {u'level': [u'participant']}
        response = c.post(url, post_dict, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], 'http://testserver/register/p/step3/')

        self.assertTrue(c.session['selected_institution'].slug == slug)
        
        return c
    
    def regStep2_respondent(self, c, slug):
        
        url = '/register/step2/'

        post_dict = {}
        response = c.get(url, post_dict)
        self.assertTrue(response.status_code == 200)

        post_dict = {u'level': [u'respondent']}
        response = c.post(url, post_dict, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], 'http://testserver/register/r/step3/')

        self.assertTrue(c.session['selected_institution'].slug == slug)
        
        return c
        
    def regStep3_participant(self, c, slug):
        """
           Run test up to step 3 of the participant registration process:
               Contact information
   
           return the client object
        """

        # Contact Information

        url = '/register/p/step3/'

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
        
        self.assertTrue(c.session['selected_institution'].slug == slug)

        return c
    
    def regStep3_respondent(self, c, slug):
        """
           Run test up to step 3 of the respondent registration process:
               Contact information
   
           return the client object
        """

        # Contact Information

        url = '/register/r/step3/'

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
                   }
        response = c.post(url, post_dict, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], 'http://testserver/register/survey/')
        self.assertTrue(c.session['selected_institution'].slug == slug)

        return c
   
    def testPayLater(self):
        """
           Test the ConfirmClassView
               - Handles a basic HTTP request w/out 500
               - Processes the form and returns a redirect to step 2
        """
        
        print "Testing Pay Later"

        c = self.regStep1(24394, 'okanagan-college-bc')
        c = self.regStep2_participant(c, 'okanagan-college-bc')
        c = self.regStep3_participant(c, 'okanagan-college-bc')
        
        # confirm that it hasn't been created yet
        self.assertTrue(c.session['selected_institution'].id == None)

        # Test Payment
        url = '/register/p/step4/'

        # Empty Query
        post_dict = {}
        response = c.get(url, post_dict)
        self.assertTrue(response.status_code == 200)

        # Pay Later
        post_dict = {'confirm': u'on',}
        response = c.post(url, post_dict)
        self.assertTrue(response.status_code == 302)
        self.assertTrue(len(mail.outbox) == 2)
        
        # Check payments
        institution = Institution.objects.get(aashe_id=24394)
#        p = Payment.objects.get(submissionset__institution=institution)
#        self.assertEqual(p.reason, "member_reg")

        self.assertEqual(SubscriptionPayment.objects.filter(subscription__institution=institution).count(), 0)
   
    def testRespondent(self):
        """
           Test the ConfirmClassView
               - Handles a basic HTTP request w/out 500
               - Processes the form and returns a redirect to step 2
        """
        
        print "Testing Respondent Registration"

        slug = 'florida-national-college-fl'
        c = self.regStep1(16384, slug)
        c = self.regStep2_respondent(c, slug)
        c = self.regStep3_respondent(c, slug)
        
        # confirm that the institution has been created
        self.assertNotEqual(c.session['selected_institution'].id, None)
        
        # Check payments
        institution = Institution.objects.get(aashe_id=16384)
        self.assertEqual(institution.slug, slug)
#        p = Payment.objects.get(submissionset__institution=institution)
#        self.assertEqual(p.reason, "member_reg")
    
    def testPayLaterInternational(self):
        """
           Test the ConfirmClassView
               - Handles a basic HTTP request w/out 500
               - Processes the form and returns a redirect to step 2
        """
        
        print "Testing Pay Later International"

        c = self.regInternational("Dummy Institution", 'dummy-institution')
        c = self.regStep3_participant(c, 'dummy-institution')
        self.assertTrue(c.session['selected_institution'].international)

        # Email notifications
        self.assertEqual(len(mail.outbox), 2)
        
        # Check payments
        institution = Institution.objects.get(name='Dummy Institution')
       
    # def testPayWithCard(self):
    #     """
    #        Test the ConfirmClassView
    #            - Handles a basic HTTP request w/out 500
    #            - Processes the form and returns a redirect to step 2
    #     """
    # 
    #     c = self.regStep2(16384, 'florida-national-college-fl')
    # 
    #     # Test Payment
    #     url = '/register/step3/'
    # 
    #     # Empty Query
    #     post_dict = {}
    #     response = c.get(url, post_dict)
    #     self.assertTrue(response.status_code == 200)
    # 
    #     post_dict = {
    #                    'name_on_card': 'Test Person',
    #                    'card_number': '4007000000027',
    #     #                        'card_number': '4222222222222',
    #                    'exp_month': str(date.today().month),
    #                    'exp_year': str(date.today().year + 1),
    #                    'cv_code': '123',
    #                    'billing_address': '123 Stree rd',
    #                    'billing_city': "Providence",
    #                    'billing_state': 'RI',
    #                    'billing_zipcode': '01234',
    #                 }
    #     response = c.post(url, post_dict)
    #     self.assertTrue(response.status_code == 302)
    #     self.assertTrue(len(mail.outbox) == 2)
    
  #   def testPayment(self):
  #         
  #         login = settings.REAL_AUTHORIZENET_LOGIN
  #         key = settings.REAL_AUTHORIZENET_KEY
  #         server = settings.REAL_AUTHORIZENET_SERVER
  #         
  #         # Test payment
  #         invoice = random.random()
  #         today = date.today()
  #         payment_dict = {
  # #                            'cc_number': '4007000000027',
  #                             'cc_number': '4222222222222',
  #                             'exp_date': "%d%d" % (today.month, (today.year+1)),
  #                             'cv_number': '123',
  #                             'billing_address': '123 Street Rd',
  #                             'billing_address_line_2': '',
  #                             'billing_city': 'City',
  #                             'billing_state': 'ST',
  #                             'billing_zipcode': '12345',
  #                             'country': "USA",
  #                             'billing_firstname': "first name",
  #                             'billing_lastname': 'last name',
  #                             'description': "%s STARS Registration" % "BOGUS INSTITUTION",
  #                         }
  #         product_list = [{'name': 'test', 'price': 1, 'quantity': 1},]
  #         response = process_payment(
  #                                    payment_dict,
  #                                    product_list,
  #                                    invoice_num=invoice,
  #                                    server=server,
  #                                    login=login,
  #                                    key=key
  #                                    )
  #         print >> sys.stderr, response
  #         self.assertTrue(response['cleared'] == True)
  #         self.assertTrue(response['trans_id'] != None)
        
        # Test duplicate transactions
        # Duplicate transactions aren't detected in test mode
#        response = process_payment(
#                                   payment_dict,
#                                   product_list,
#                                   invoice_num=invoice,
#                                   server=server,
#                                   login=login,
#                                   key=key
#                                   )
#        print >> sys.stderr, response
#        self.assertTrue(response['cleared'] == False)
#        self.assertTrue(response['msg'] == 'A duplicate transaction has been submitted.')
        
        # multiple products
#        product_list = [{'name': 'test', 'price': 1, 'quantity': 2},]
#        response = process_payment(payment_dict,
#                                   product_list,
#                                   invoice_num=invoice,
#                                   server=server,
#                                   login=login,
#                                   key=key
#                                   )
#        print >> sys.stderr, response
#        self.assertTrue(response['cleared'] == True)
#        self.assertTrue(response['trans_id'] != None)
        
        
