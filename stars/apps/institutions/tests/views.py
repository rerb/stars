"""Tests for apps.institutions.views.
"""
from unittest import TestCase

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest
import testfixtures

from stars.apps.institutions.models import Institution
from stars.apps.institutions import views


class SubmissionInquiryViewTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.user = User(username='sophisticate')
        self.user.save()
        self.request.user = self.user
        self.request.session = {}
        self.request.META['REMOTE_ADDR'] = '10.0.0.1'

        self.institution = Institution.objects.create()
        self.institution.save()

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def tearDown(self):
        self.user.delete()
        self.institution.delete()

    def test_process_forms_invalid_recaptcha_response_error_message(self):
        """Does process_forms display an error msg for invalid recaptcha resp?
        """
        submission_inquiry_view = views.SubmissionInquiryView()

        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.views.SubmissionInquiryView.'
                      'get_form_list',
                      lambda x,y,z : ({ 'inquirer_details': MockWithIsValid(True),
                                   'credit_inquiries': MockWithIsValid(True) },
                                   dict()))
            r.replace('stars.apps.institutions.views.captcha',
                      MockInvalidCaptcha)
            context, _ = submission_inquiry_view.process_forms(
                self.request, { 'institution': self.institution })
        # calling get_success_response just to generate a response
        # from self.request:
        response = submission_inquiry_view.get_success_response(
            self.request, context)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('Captcha Message didn\'t validate' in
                        error_message_divs[0].text)

    def test_process_forms_invalid_form_error_message(self):
        """Does process_forms display an error msg for invalid form input?
        """
        submission_inquiry_view = views.SubmissionInquiryView()

        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.views.SubmissionInquiryView.'
                      'get_form_list',
                      lambda x,y,z : ({ 'inquirer_details': MockWithIsValid(False),
                                   'credit_inquiries': MockWithIsValid(True) },
                                   dict()))
            r.replace('stars.apps.institutions.views.captcha',
                      MockValidCaptcha)
            context, _ = submission_inquiry_view.process_forms(
                self.request, { 'institution': self.institution })
        # calling get_success_response just to generate a response
        # from self.request:
        response = submission_inquiry_view.get_success_response(
            self.request, context)
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)

class MockWithIsValid(object):

    def __init__(self, is_valid=False, is_valid_lambda=True):
        if is_valid_lambda:
            self.is_valid = lambda : is_valid
        else:
            self.is_valid = is_valid
        self.email_address = 'fannymcquiston@example.com'
        self.error_code = '88'

    def save(self, *args, **kwargs):
        return MockWithIsValid()


class MockInvalidCaptcha(object):

    @classmethod
    def submit(klass, *args, **kwargs):
        return MockWithIsValid(is_valid=False, is_valid_lambda=False)


class MockValidCaptcha(object):

    @classmethod
    def submit(klass, *args, **kwargs):
        return MockWithIsValid(is_valid=True, is_valid_lambda=False)
