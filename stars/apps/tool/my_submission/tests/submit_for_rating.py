"""
    Doctests for the submit for rating tool that will process an institutions
    submission and notify the liason and STARS Staff

    Test premises:
        - the forms are processed correctly
            - Confirmation form
            - Letter Submission
            - Finalize
        - email notifications are sent
"""
from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.conf import settings

from stars.apps.submissions.models import SubmissionSet

import sys, os

class RatingTest(TestCase):
    fixtures = ['submit_for_rating_tests.json','notification_emailtemplate_tests.json']

    def setUp(self):

        settings.CELERY_ALWAYS_EAGER = True

        ss = SubmissionSet.objects.get(pk=1)
        ss.save()

    def test_process(self):

        c = Client()
        c.login(username='test_user', password='test')

        self.confirmView(c)
        self.letterView(c)
        self.finalizeView(c)


    def confirmView(self, c):
        """
            Test the ConfirmClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and returns a redirect to step 2
        """

        print >> sys.stderr, "TESTING: Confirm Submission"

        post_dict = {}
        response = c.get('/tool/submissions/submit/', post_dict)
        print response.status_code
        self.assertTrue(response.status_code == 200)

        post_dict = {'submission_boundary': 'boundary text',}
        response = c.post('/tool/submissions/submit/', post_dict, follow=False)
        self.assertTrue(response.status_code == 302)

    def letterView(self, c):
        """
            Tests the LetterClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and redirects to step 3
        """

        print >> sys.stderr, "TESTING: Letter"

        post_dict = {}
        response = c.get('/tool/submissions/submit/letter/', post_dict)
        self.assertTrue(response.status_code == 200)

        f = open(os.path.join(os.path.dirname(__file__), 'test.pdf'))

        post_dict = {
                        'letter_form-presidents_letter': f,
                        'exec_contact_form-executive_contact_first_name': 'First',
                        'exec_contact_form-executive_contact_last_name': 'Last',
                        'exec_contact_form-executive_contact_title': 'Title',
                        'exec_contact_form-executive_contact_department': 'Dept.',
                        'exec_contact_form-executive_contact_email': 'test@test.edu',
                        'exec_contact_form-executive_contact_address': 'Address',
                        'exec_contact_form-executive_contact_city': 'City',
                        'exec_contact_form-executive_contact_state': 'ST',
                        'exec_contact_form-executive_contact_zip': '12345',
                        'exec_contact_form-confirm': 'on'
                    }
        response = c.post('/tool/submissions/submit/letter/', post_dict, follow=False)

        self.assertTrue(response.status_code == 302)

    def finalizeView(self, c):
        """
            Tests the LetterClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and saves the SubmissionSet object
                - Sends emails to liason, user and stars staff
        """

        print >> sys.stderr, "TESTING: Finalize"

        post_dict = {}
        response = c.get('/tool/submissions/submit/finalize/', post_dict)
        self.assertTrue(response.status_code == 200)

        post_dict = {'confirm': 1,}
        response = c.post('/tool/submissions/submit/finalize/', post_dict, follow=False)
        self.assertTrue(response.status_code == 200)
        ss = SubmissionSet.objects.get(pk=1)
        self.assertTrue(ss.status == 'r')
        # one email to institution
        self.assertTrue(len(mail.outbox) == 2)
