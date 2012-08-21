"""Tests for stars.apps.accounts.mixins.SubmissionMixin.
"""
from unittest import TestCase

from django.contrib.auth.models import AnonymousUser
from testfixtures import LogCapture

from dummy_request import DummyRequest
from stars.apps.institutions.models import Institution
from stars.apps.accounts.mixins import SubmissionMixin


class SubmissionMixinSubclass(SubmissionMixin):

    pass


class SubmissionMixinTest(TestCase):

    def setUp(self):
        institution = Institution(name='Fake Institution',
                                  aashe_id='-1111',
                                  enabled=True)
        institution.save()

        anon = AnonymousUser()
        anon.account_list = ["account",]
        anon.current_inst = institution

        self.request = DummyRequest(anon)

        self.mixed_in = SubmissionMixinSubclass()

    def test_get_active_submission_problem_response_logging(self):
        """Does get_active_submission_problem_response log an error
        when there's no active submission?
        """
        with LogCapture('stars.request') as log:
            self.mixed_in.get_active_submission_problem_response(self.request)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue('No active submission' in log.records[0].msg)
