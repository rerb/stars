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
import tempfile

from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.conf import settings

from stars.apps.submissions.models import SubmissionSet


class RatingTest(TestCase):

    fixtures = ['submit_for_rating_tests.json',
                'notification_emailtemplate_tests.json']

    def setUp(self):

        settings.CELERY_ALWAYS_EAGER = True

        ss = SubmissionSet.objects.get(pk=1)
        ss.save()

    def test_process(self):

        c = Client()
        c.login(username='test_user', password='test')

        import pdb; pdb.set_trace()

        self.confirmView(c)
        self.letterView(c)
        self.finalizeView(c)


    def confirmView(self, c):
        """
            Test the ConfirmClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and returns a redirect to step 2
        """
        response = c.get('/tool/submissions/submit/')
        self.assertTrue(response.status_code == 302)

    def letterView(self, c):
        """
            Tests the LetterClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and redirects to step 3
        """

        response = c.get('/tool/submissions/submit/letter/')
        self.assertTrue(response.status_code == 200)

        pdf_file = tempfile.TemporaryFile()
        letter_file = tempfile.TemporaryFile()
        letter_file.write('Some text just for the hell of it')
        letter_file.seek(0)

        post_dict = {
            'letter_form-presidents_letter': pdf_file,
            'exec_contact_form-president_first_name': 'First',
            'exec_contact_form-president_last_name': 'Last',
            'exec_contact_form-president_title': 'Title',
            'exec_contact_form-department': 'Dept.',
            'exec_contact_form-email': 'test@test.edu',
            'exec_contact_form-president_address': 'Address',
            'exec_contact_form-president_city': 'City',
            'exec_contact_form-president_state': 'ST',
            'exec_contact_form-president_zip': '12345',
            'exec_contact_form-confirm': 'on',
            'letter_form-presidents_letter': letter_file
            }
        response = c.post('/tool/submissions/submit/letter/', post_dict,
                          follow=False)

        self.assertTrue(response.status_code == 302)

    def finalizeView(self, c):
        """
            Tests the LetterClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and saves the SubmissionSet object
                - Sends emails to liason, user and stars staff
        """

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
