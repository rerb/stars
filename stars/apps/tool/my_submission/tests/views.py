"""Tests for apps.tool.my_submission.views.
"""
from django.utils.unittest import TestCase

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest
from django.shortcuts import render
from django.template import RequestContext
import testfixtures

from stars.apps.tool.my_submission import views
from stars.apps.tool.tests.views import (InstitutionToolMixinTest,
                                         UserCanEditSubmissionMixinTest)
from stars.test_factories import (InstitutionFactory,
                                  StarsAccountFactory,
                                  SubmissionSetFactory)


# @TODO - we definitely need tests here for all the form submission tools

class SubmissionSummaryViewTest(InstitutionToolMixinTest):

    view_class = views.SubmissionSummaryView
    blessed_user_level = 'submit'  # user_level that should be allowed to GET
    blocked_user_level = 'view'  # user_level that should be blocked

    def setUp(self):
        super(SubmissionSummaryViewTest, self).setUp()
        self.institution = InstitutionFactory()
        self.account = StarsAccountFactory(institution=self.institution)
        self.request.user = self.account.user
        self.submission = SubmissionSetFactory(institution=self.institution)

    def test_get_succeeds(self, **kwargs):
        super(InstitutionToolMixinTest, self).test_get_succeeds(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))

    def test_get_is_blocked(self, **kwargs):
        super(InstitutionToolMixinTest, self).test_get_is_blocked(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))

    def test_success_url_is_loadable(self, **kwargs):
        super(InstitutionToolMixinTest, self).test_get_is_blocked(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))


class EditBoundaryViewTest(UserCanEditSubmissionMixinTest):

    view_class = views.EditBoundaryView
