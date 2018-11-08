"""

    # SC Application

"""

from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.core.urlresolvers import reverse

from stars.apps.custom_forms.models import SteeringCommitteeNomination

import os


class SCAppTest(TestCase):
    fixtures = ['notification_emailtemplate_tests.json', ]

    def setUp(self):
        self.c = Client()
        self.f = open(os.path.join(os.path.dirname(__file__), '__init__.py'))
        self.post_dict = {
            'first_name': 'ben',
            'last_name': 'stookey',
            'phone_number': '800 555 1212',
            'email': 'test@aashe.org',
            'affiliation': 'institution',
            'why': 'Why not?',
            'skills': 'mad skilz',
            'successful': 'of course',
            'strengths': 'mind',
            'perspectives': 'blah blah',
            'resume': self.f,
        }
        self.url = reverse('steering-committee-nomination')

    def testFormSubmission(self):
        """
            Tests:
                - Request returns 200 status code
                - Form saves the SC model
                - view sends email
        """
        self.assertEqual(SteeringCommitteeNomination.objects.count(), 0)

        response = self.c.post(self.url, self.post_dict)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(SteeringCommitteeNomination.objects.count(), 1)
