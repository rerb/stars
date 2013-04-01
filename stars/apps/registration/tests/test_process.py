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

from datetime import date

from stars.apps.institutions.models import (Institution,
                                            Subscription,
                                            SubscriptionPayment)
from stars.apps.registration.models import ValueDiscount


class TestProcess(TestCase):

    fixtures = ['registration_tests.json', 'iss_testdata.json',
                'notification_emailtemplate_tests.json']

    multi_db = True

    def setUp(self):

        print "***Testing Registration"

        self.test_inst_aashe_id = 24394
        self.test_inst_slug = 'okanagan-college-bc'

        self.url = '/register/'

        self.liaison_contact_dict = {
            'contact-contact_first_name': 'ben',
            'contact-contact_middle_name': 'wood',
            'contact-contact_last_name': 'stookey',
            'contact-contact_title': 'title',
            'contact-contact_department': 'dept.',
            'contact-contact_phone': '1231231234',
            'contact-contact_email': 'stars_test_liaison@aashe.org'}

        self.exec_contact_dict = {
            'contact-executive_contact_first_name': 'ben',
            'contact-executive_contact_middle_name': 'wood',
            'contact-executive_contact_last_name': 'stookey',
            'contact-executive_contact_title': 'title',
            'contact-executive_contact_department': 'dept.',
            'contact-executive_contact_email': 'stars_test_exec@aashe.org'}

        self.payment_dict = {
            'payment-name_on_card': u'ben',
            'payment-card_number': u'4007000000027',
            'payment-exp_month': u'12',
            'payment-exp_year': unicode(date.today().year + 1),
            'payment-cv_code': u'123',
            'payment-billing_address': u'123 Street st.',
            'payment-billing_city': u'Newport',
            'payment-billing_state': u'RI',
            'payment-billing_zipcode': u'02840',
            'payment-discount_code': u'STARS-TEST'}

        discount = ValueDiscount(code='STARS-TEST', amount=200,
                           start_date=date.today(), end_date=date.today())
        discount.save()

    def testRespondent(self):
        """
            Runs through registration as a respondent
        """
        print "***Testing Respondent"

        c = Client()
        c.login(username='test_user', password='test')

        self.assertEqual(0, Institution.objects.count())
        self.assertEqual(0, Subscription.objects.count())
        self.assertEqual(0, SubscriptionPayment.objects.count())

        # Step 1: Select institution
        post_dict = {}
        response = c.get(self.url, post_dict)
        self.assertTrue(response.status_code == 200)
        post_dict = {'registration_wizard-current_step': 'select',
                     'select-aashe_id': self.test_inst_aashe_id}
        response = c.post(self.url, post_dict)
        self.assertTrue(response.status_code == 200)

        # Step 2: Participation level
        post_dict = {'registration_wizard-current_step': 'level',
                     'level-level': 'respondent'}
        response = c.post(self.url, post_dict)
        self.assertTrue(response.status_code == 200)

        # Step 3: Contact information
        post_dict = {'registration_wizard-current_step': 'contact'}
        post_dict.update(self.liaison_contact_dict)
        response = c.post(self.url, post_dict)
        # redirected to survey
        self.assertTrue(response.status_code == 302)
        self.assertEqual(response._headers['location'][1],
                         "http://testserver/register/%s/survey/" %
                         self.test_inst_slug)

        # two emails sent out
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [u'stars_test_liaison@aashe.org',
                                             'stars_test_user@aashe.org'])

        self.assertEqual(1, Institution.objects.count())
        self.assertEqual(0, Subscription.objects.count())
        self.assertEqual(0, SubscriptionPayment.objects.count())

    def participantFirstSteps(self, c):
        """
            The first three steps are shared by the pay later
            and pay now options
        """

        # Step 1: Select institution
        post_dict = {}
        response = c.get(self.url, post_dict)
        self.assertTrue(response.status_code == 200)
        post_dict = {'registration_wizard-current_step': 'select',
                     'select-aashe_id': self.test_inst_aashe_id}
        response = c.post(self.url, post_dict)
        self.assertTrue(response.status_code == 200)

        # Step 2: Participation level
        post_dict = {'registration_wizard-current_step': 'level',
                     'level-level': 'participant'}
        response = c.post(self.url, post_dict)
        self.assertTrue(response.status_code == 200)

        # Step 3: Contact information
        post_dict = {'registration_wizard-current_step': 'contact'}
        post_dict.update(self.liaison_contact_dict)
        post_dict.update(self.exec_contact_dict)
        response = c.post(self.url, post_dict)
        self.assertTrue(response.status_code == 200)

    def testParticipantPayLater(self):
        """
            participant registering and selecting to pay later

            @todo - this needs to test for required fields
        """
        print "***Testing ParticipantPayLater"

        c = Client()
        c.login(username='test_user', password='test')

        self.assertEqual(0, Institution.objects.count())
        self.assertEqual(0, Subscription.objects.count())
        self.assertEqual(0, SubscriptionPayment.objects.count())

        self.participantFirstSteps(c)

        # Step 4: Payment (pay later)
        post_dict = {'registration_wizard-current_step': 'payment',
                     'payment-pay_later': u'on'}
        response = c.post(self.url, post_dict)

        # redirected to survey
        self.assertTrue(response.status_code == 302)
        self.assertEqual(response._headers['location'][1],
                         "http://testserver/register/%s/survey/" %
                         self.test_inst_slug)

        # two emails sent out
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [u'stars_test_liaison@aashe.org',
                                             'stars_test_user@aashe.org'])
        self.assertEqual(mail.outbox[1].to, [u'stars_test_exec@aashe.org'])

        self.assertEqual(1, Institution.objects.count())
        self.assertEqual(1, Subscription.objects.count())
        self.assertEqual(0, SubscriptionPayment.objects.count())

    def testParticipantPayNow(self):
        """
            participant registering and selecting to pay now

            @todo - this needs to test for required fields
        """
        print "***Testing ParticipantPayNow"

        c = Client()
        c.login(username='test_user', password='test')

        self.assertEqual(0, Institution.objects.count())
        self.assertEqual(0, Subscription.objects.count())
        self.assertEqual(0, SubscriptionPayment.objects.count())

        self.participantFirstSteps(c)

        # Step 4: Payment
        post_dict = {'registration_wizard-current_step': 'payment'}
        post_dict.update(self.payment_dict)

        # bogus card
        post_dict['payment-card_number'] = u'1212121212121'
        response = c.post(self.url, post_dict)
        self.assertEqual(response.status_code, 200)

        # test card should pass
        post_dict['payment-card_number'] = u'4007000000027'
        response = c.post(self.url, post_dict)

        # redirected to survey
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1],
                         "http://testserver/register/%s/survey/" %
                         self.test_inst_slug)

        # two emails sent out to participants
        # one email sent out for the errored card #
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[1].to, [u'stars_test_liaison@aashe.org',
                                             'stars_test_user@aashe.org'])
        self.assertEqual(mail.outbox[2].to, [u'stars_test_exec@aashe.org'])

        self.assertEqual(1, Institution.objects.count())
        self.assertEqual(1, Subscription.objects.count())
        self.assertEqual(1, SubscriptionPayment.objects.count())

        # test survey
        url = ("http://testserver/register/%s/survey/" %
                         self.test_inst_slug)
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        post_dict = {}
        response = c.post(url, post_dict)
        self.assertEqual(response._headers['location'][1],
                         "http://testserver/tool/%s/" %
                         self.test_inst_slug)
