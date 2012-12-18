"""Tests for apps.tool.my_submission.views.
"""
from unittest import TestCase

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest
from django.shortcuts import render
from django.template import RequestContext
import testfixtures

from stars.apps.tool.my_submission import views
from stars.apps.credits.models import Credit
from stars.apps.submissions.models import CreditSubmission, SubmissionSet
from stars.apps.tool.tests.views import UserCanEditSubmissionMixinTest
from stars.test_factories import UserFactory


class SaveSnapshotTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.user = UserFactory()
        self.request.user = self.user
        self.request.session = {}

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def test_render_to_response_missing_boundary_error_message(self):
        """Does render_to_response display an error if there's no boundary?
        """
        save_snapshot = views.SaveSnapshot()
        save_snapshot.request = self.request
        context = RequestContext(self.request,
                                 { 'active_submission': SubmissionSet() })
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.tool.my_submission.views.user_can_submit_snapshot',
                lambda x,y: True)
            response = save_snapshot.render_to_response(context)
        response = self.message_middleware.process_response(self.request,
                                                            response)
        self.assertTrue('messages' in response.cookies.keys())
        self.assertTrue('must complete your Boundary' in
                        response.cookies['messages'].js_output())


class ConfirmClassViewTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.user = UserFactory()
        self.request.user = self.user
        self.request.session = {}
        self.submissionset = SubmissionSet(creditset_id=-999,
                                           institution_id=-999,
                                           registering_user_id=-999,
                                           date_registered='1999-01-01')
        self.submissionset.save()

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def test_render_to_response_missing_boundary_error_message(self):
        """Does render_to_response display an error if there's no boundary?
        """
        confirm_class_view = views.ConfirmClassView()
        confirm_class_view.request = self.request
        context = RequestContext(self.request,
                                 { 'active_submission': self.submissionset })
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.tool.my_submission.views.'
                      'user_can_submit_for_rating',
                      lambda x,y: True)
            response = confirm_class_view.render_to_response(context)
        response = self.message_middleware.process_response(self.request,
                                                            response)
        self.assertTrue('messages' in response.cookies.keys())
        self.assertTrue('must complete your Boundary' in
                        response.cookies['messages'].js_output())


class TopLevelTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.user = UserFactory()
        self.request.user = self.user
        self.request.session = {}

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def test_credit_detail_warnings(self):
        """Does credit_detail show warning messages if ...form.has_warnings()?
        """
        self.request.user = MockUser()
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.accounts.decorators._get_account_problem_response',
                lambda x: False)
            r.replace('stars.apps.tool.my_submission.views.'
                      '_get_credit_submission_context',
                      lambda w,x,y,z : RequestContext(
                          self.request,
                          {'credit_submission': CreditSubmission(
                              credit=Credit()),
                           'credit': None}))
            r.replace('stars.apps.tool.my_submission.views.basic_save_form',
                      lambda w,x,y,z,fail_msg : (MockCreditSubmissionForm(),
                                                 None))
            r.replace('stars.apps.tool.my_submission.views.respond',
                      lambda x,y,context : context)
            context = views.credit_detail(self.request, None, None, None)
        response = render(self.request, 'base.html', context)
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('data values are not' in info_message_divs[0].text)


class MockCreditSubmissionForm(object):

    def has_warnings(self):
        return True


class MockUser(object):

    def has_perm(self, *args):
        return True


class SubmissionSummaryViewTest(UserCanEditSubmissionMixinTest):

    view_class = views.SubmissionSummaryView
