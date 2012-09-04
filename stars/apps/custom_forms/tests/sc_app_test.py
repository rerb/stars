"""

    # SC Application

"""

from django.test import TestCase
from django.core import mail
from django.test.client import Client

from stars.apps.custom_forms.models import SteeringCommitteeNomination

import os


class SCAppTest(TestCase):
    fixtures = ['notification_emailtemplate_tests.json',]

    def setUp(self):
        pass

    def testFormSubmission(self):
        """
            Tests:
                - Request returns 200 status code
                - Form saves the SC model
                - view sends email
        """
        self.assertTrue(SteeringCommitteeNomination.objects.count() == 0)

        c = Client()
        f = open(os.path.join(os.path.dirname(__file__), '__init__.py'))
        post_dict = {
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
            'resume': f,
        }
        response = c.post('/cfm/sc-app/', post_dict)

        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(mail.outbox) == 1)
        self.assertTrue(SteeringCommitteeNomination.objects.count() == 1)
