"""

    # TA Application 
    
"""

from django.test import TestCase
from django.core import mail
from django.test.client import Client

from stars.apps.custom_forms.models import TAApplication
from stars.apps.credits.models import Subcategory

import sys, os

class TAAppTest(TestCase):
    fixtures = ['credits_testdata.json','notification_emailtemplate_tests.json']

    def setUp(self):
        pass

    def testOverdueList(self):
        """
            Tests:
                - Request returns 200 status code
                - Form saves the TA model
                - view sends email
        """
        self.assertTrue(TAApplication.objects.count() == 0)
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
            'subcategories': ['1',],
            'skills_and_experience': 'blah blah',
            'related_associations': 'blah blah',
            'resume': f,
            'credit_weakness': 'blah blah',
        }
        response = c.post('/cfm/ta-app/', post_dict)
        
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(mail.outbox) == 1)
        self.assertTrue(TAApplication.objects.count() == 1)

"""
    >>> import os
    
    >>> from django.core.management import call_command
    >>> from django.core import mail
    >>> from django.test.client import Client
    
    >>> from stars.apps.custom_forms.models import TAApplication
    
    >>> call_command("loaddata", "' + 'credits_testdata.json' + '", verbosity=0)
    
    >>> c = Client()
    >>> f = open(os.path.join(os.path.dirname(__file__), '__init__.py'))
    >>> response = c.post('/cfm/ta-app/', {
    ...     'first_name': 'ben',
    ...     'last_name': 'stookey',
    ...     'title': 'title',
    ...     'department': 'dept',
    ...     'institution': 'inst',
    ...     'phone_number': '800 555 1212',
    ...     'email': 'test@aashe.org',
    ...     'address': 'addy',
    ...     'city': 'city',
    ...     'state': 'ST',
    ...     'zipcode': '01234',
    ...     'institution_type': '2-year',
    ...     'subcategories': ['1',],
    ...     'skills_and_experience': 'blah blah',
    ...     'related_associations': 'blah blah',
    ...     'resume': f,
    ...     'credit_weakness': 'blah blah',
    ...     })
    >>> response.status_code
    200
    >>> len(mail.outbox)
    1
    >>> TAApplication.objects.count()
    1

"""
