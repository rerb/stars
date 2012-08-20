"""Tests for stars.apps.accounts.utils.
"""
from unittest import TestCase

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.shortcuts import render
import testfixtures

from dummy_request import DummyRequest
from stars.apps.institutions.models import Institution
from stars.apps.accounts import utils


class UtilsTest(TestCase):

    def setUp(self):
        institution = Institution(name='Fake Institution',
                                  aashe_id='-111111',
                                  enabled=True)

        anon = AnonymousUser()
        anon.account_list = ["account",]
        anon.current_inst = institution
        anon.is_staff = True
        anon.is_authenticated = lambda : True

        self.request = DummyRequest(anon)
        self.request.session = {'current_inst_pk': 999999999}
        self.request.COOKIES = {'current_inst': 99999999}

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def test__get_account_from_session_missing_inst_logging(self):
        """Does _get_account_from_session log an error if there's no inst?
        """
        with testfixtures.LogCapture('stars') as log:
            utils._get_account_from_session(self.request)

        self.assertEqual(len(log.records), 2)
        for record in log.records:
            self.assertEqual(record.levelname, 'ERROR')
            self.assertTrue('titution not found' in record.msg)

    def test__get_account_from_session_missing_inst_error_message(self):
        """Does _get_account_from_session show an error msg if there's no inst?
        """
        utils._get_account_from_session(self.request)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('titution not found' in error_message_divs[0].text)
