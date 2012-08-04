"""Tests for stars.apps.accounts.utils.
"""
from unittest import TestCase

from django.contrib.auth.models import AnonymousUser
import testfixtures

from dummy_request import DummyRequest
from stars.apps.institutions.models import Institution
from stars.apps.accounts import utils


class UtilsTest(TestCase):

    def setUp(self):
        institution = Institution(name='Fake Institution',
                                  aashe_id='-111111',
                                  enabled=True)
        institution.save()

        anon = AnonymousUser()
        anon.account_list = ["account",]
        anon.current_inst = institution
        anon.is_staff = True

        self.request = DummyRequest(anon)

    def test__get_account_from_session_logging(self):
        """Does _get_account_from_session log an error
        when there's no active submission?
        """
        self.request.session = {'current_inst_pk': 999999999}
        self.request.COOKIES = {'current_inst': 99999999}

        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace(
                    'django.contrib.auth.models.AnonymousUser.is_authenticated',
                    lambda x: True)
                utils._get_account_from_session(self.request)

        self.assertEqual(len(log.records), 2)
        for record in log.records:
            self.assertEqual(record.levelname, 'ERROR')
            self.assertTrue(record.module_path.startswith('stars'))
            self.assertTrue('institution not found' in record.msg)
