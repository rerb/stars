"""Tests for stars.apps.accounts.aashe.AASHEAuthBackend.
"""
from unittest import TestCase

from django.contrib.auth.models import User
from testfixtures import LogCapture

from stars.apps.accounts.aashe import AASHEAuthBackend


class AASHEAuthBackendTest(TestCase):

    def setUp(self):
        self.aashe_auth_backend = AASHEAuthBackend()
        self.user = User()

    def test_has_perm_logging(self):
        """Does has_perm() log an error when asked to check a non-existent
        permission?
        """
        self.user.is_authenticated = True
        self.user.is_staff = False
        self.user.account = 1

        with LogCapture('stars.user') as log:
            self.aashe_auth_backend.has_perm(self.user, 'bo-o-o-o-gus!')

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue('bo-o-o-o-gus' in log.records[0].msg)
