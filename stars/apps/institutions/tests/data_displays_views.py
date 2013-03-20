"""Tests for apps.institutions.data_displays.views.
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
from stars.apps.institutions.data_displays import views


class AggregateFilterTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.user = User(username='sophisticate')
        self.user.save()
        self.request.user = self.user
        self.request.session = {}

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def tearDown(self):
        self.user.delete()

    def test_form_invalid_error_message(self):
        """Does form_invalid display an error message?
        """
        aggregate_filter = views.AggregateFilter()
        aggregate_filter.request = self.request
        response = aggregate_filter.form_invalid(None)
        response.render()
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)


class ScoreFilterTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.user = User(username='sophisticate')
        self.user.save()
        self.request.user = self.user
        self.request.session = {}

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def tearDown(self):
        self.user.delete()

    def test_form_invalid_error_message(self):
        """Does form_invalid display an error message?
        """
        score_filter = views.ScoreFilter()
        score_filter.request = self.request
        response = score_filter.form_invalid(None)
        response.render()
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)


class ContentFilterTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.user = User(username='sophisticate')
        self.user.save()
        self.request.user = self.user
        self.request.session = {}

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def tearDown(self):
        self.user.delete()

    def test_form_invalid_error_message(self):
        """Does form_invalid display an error message?
        """
        content_filter = views.ContentFilter()
        content_filter.request = self.request
        response = content_filter.form_invalid(None)
        response.render()
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)
