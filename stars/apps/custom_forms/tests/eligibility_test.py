"""
    Test cases for 'eligibility-inquiry' url.
"""
from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.client import Client


class EligibilityTest(TestCase):
    fixtures = ['notification_emailtemplate_tests.json']

    def setUp(self):
        self.c = Client()
        self.post_dict = {
            'name': 'ben',
            'title': 'title',
            'email': 'test@aashe.org',
            'institution': 'inst',
            'phone_number': '800 555 1212',
            'rationale': 'just because'
        }

    def test_200_status_code(self):
        """Does 'eligibility-inquiry' return a 200?
        """
        response = self.c.post(reverse('eligibility-inquiry'),
                               self.post_dict)

        self.assertEqual(response.status_code, 200)

    def test_mail_sent(self):
        """Do two emails get sent?
        """
        outgoing_mails = len(mail.outbox)
        self.c.post(reverse('eligibility-inquiry'), self.post_dict)

        self.assertEqual((len(mail.outbox) - outgoing_mails), 2)
