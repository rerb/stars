"""
    # TA Application
"""

from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.client import Client

from stars.apps.custom_forms.models import TAApplication
from stars.apps.credits.models import Subcategory

import os
import sys
import unittest


class TAAppTest(TestCase):
    fixtures = ['credits_testdata.json',
                'notification_emailtemplate_tests.json']

    def setUp(self):
        self.c = Client()
        f = open(os.path.join(os.path.dirname(__file__), '__init__.py'))
        self.post_dict = {
            'first_name': 'ben',
            'last_name': 'stookey',
            'title': 'title',
            'department': 'dept',
            'institution': 'inst',
            'phone_number': '800 555 1212',
            'email': 'test@aashe.org',
            'instituion_type': '2-year',
            'subcategories': ['1', ],
            'skills_and_experience': 'blah blah',
            'related_associations': 'blah blah',
            'resume': f,
            'credit_weakness': 'blah blah',
        }

    def test_200_status_code(self):
        """
        Is there a 200 on POST
        """
        # Travis cannot find a file to open, so skip it.
        if '--liveserver=' in sys.argv:
            raise unittest.SkipTest()
        response = self.c.post(reverse('technical-advisor-application'),
                               self.post_dict)
        self.assertEqual(response.status_code, 200)

    def test_mail_sent(self):
        """
        Does an email get sent?
        """
        # Travis cannot find a file to open, so skip it.
        if '--liveserver=' in sys.argv:
            raise unittest.SkipTest()
        outgoing_mails = len(mail.outbox)
        self.c.post(reverse('technical-advisor-application'), self.post_dict)
        self.assertEqual((len(mail.outbox) - outgoing_mails), 1)

    def test_application_saved(self):
        """
        Is the application saved?
        """
        # Travis cannot find a file to open, so skip it.
        if '--liveserver=' in sys.argv:
            raise unittest.SkipTest()
        self.c.post(reverse('technical-advisor-application'), self.post_dict)
        self.assertEqual(TAApplication.objects.count(), 1)
