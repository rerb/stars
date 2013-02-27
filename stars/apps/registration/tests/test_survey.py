"""
    Doctests for the survey view after registration

    Test premises:
        - the forms are processed correctly
            - Form loads
            - Form processes
            - Saves survey
            - View redirects
"""

from django.test import TestCase
from django.test.client import Client

from stars.apps.institutions.models import RegistrationSurvey


class TestSurvey(TestCase):
    fixtures = ['submit_for_rating_tests.json','registration_tests.json']

    def setUp(self):
        pass

    def testSurveyView(self):
        """
            Test the RegistrationSurveyView
                - Handles a basic HTTP request w/out 500
                - Processes the form and returns a redirect account
                - Saves survey
        """
        self.assertTrue(RegistrationSurvey.objects.count() == 0)

        c = Client()
        c.login(username='test_user', password='test')
        post_dict = {}
        response = c.get('/register/survey/', post_dict, follow=True)
        self.assertEqual(response.status_code, 200)

        post_dict = {
            'institution': 1,
            'user': 5215,
            'source': 'heard',
            'reasons': [1,],
            'other': 'other',
            'primary_reason': 1,
            'enhancements': 'enhance!',
        }

        response = c.post('/register/survey/', post_dict, follow=False)
        self.assertEqual(response.status_code, 302)
