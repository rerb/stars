"""

    # TA Application

"""

from django.test import TestCase
from django.core import mail
from django.test.client import Client

from stars.apps.custom_forms.models import TAApplication
from stars.apps.credits.models import Subcategory

import os


class TAAppTest(TestCase):
    fixtures = ['credits_testdata.json',
                'notification_emailtemplate_tests.json']

    def setUp(self):
        pass

    def testOverdueList(self):
        """
            Tests:
                - Request returns 200 status code
                - Form saves the TA model
                - view sends email
        """
        self.assertEqual(TAApplication.objects.count(), 0)
        self.assertTrue(Subcategory.objects.count() > 0)

        c = Client()
        f = open(os.path.join(os.path.dirname(__file__), '__init__.py'))
        post_dict = {
            'first_name': 'ben',
            'last_name': 'stookey',
            'title': 'title',
            'department': 'dept',
            'institution': 'inst',
            'phone_number': '800 555 1212',
            'email': 'test@aashe.org',
            'address': 'addy',
            'city': 'city',
            'state': 'ST',
            'zipcode': '01234',
            'instituion_type': '2-year',
            'subcategories': ['1', ],
            'skills_and_experience': 'blah blah',
            'related_associations': 'blah blah',
            'resume': f,
            'credit_weakness': 'blah blah',
        }
        response = c.post('/cfm/ta-app/', post_dict)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(TAApplication.objects.count(), 1)
