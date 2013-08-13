"""Tests for stars.apps.tool.staff_tool.views.
"""
from unittest import TestCase

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest
from django.shortcuts import render

from stars.apps.institutions.models import Institution

import testfixtures


class ViewsTest(TestCase):

    fixtures = ['subscription_payment_testdata']

    def setUp(self):
        self.request = HttpRequest()
        self.request.user = User()
        #        self.request.user.current_inst = False
        self.request.user.is_staff = True
        self.request.session = {}
        self.request.method = 'POST'
        self.institution = Institution()
        self.institution.save()

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def test_select_institution_change_failed_error_message(self):
        """Does select_institution show an error when change_institution fails?
        """
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.staff_tool.views.auth_utils.change_institution',
                lambda x,y: False)
            views.select_institution(self.request, self.institution.id)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('nable to change inst' in error_message_divs[0].text)
