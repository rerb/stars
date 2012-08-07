"""Tests for stars.apps.accounts.views.
"""
from unittest import TestCase

from django.contrib.auth.models import User
import testfixtures

from dummy_request import DummyRequest
from stars.apps.institutions.models import Institution
from stars.apps.accounts import views


class ViewsTest(TestCase):

    def setUp(self):
        user = User()
        user.account_list = ["account",]
        user.current_inst = Institution(name='Fake Institution',
                                        aashe_id='-2',
                                        enabled=True)
        self.request = DummyRequest(user)

    def test_select_school_logging(self):
        """Does select_school log a message error when there's no institution
        for the id provided?
        """
        with testfixtures.LogCapture('stars.request') as log:
            with testfixtures.Replacer() as r:
                r.replace(
                    'django.contrib.auth.models.AnonymousUser.is_authenticated',
                    lambda x: True)
                r.replace('stars.apps.accounts.views.change_institution',
                          lambda x, y: True)
                views.select_school(self.request, 999999)

        self.assertEqual(len(log.records), 1)
        for record in log.records:
            self.assertEqual(record.levelname, 'INFO')
            self.assertTrue('non-existent institution' in record.msg)

    def test_terms_of_service_logging(self):
        """Does terms_of_service log an error if there's no request.user.account?
        """
        with testfixtures.LogCapture('stars.request') as log:
            self.request.user.account = None
            views.terms_of_service(self.request)

        self.assertEqual(len(log.records), 1)
        for record in log.records:
            self.assertEqual(record.levelname, 'ERROR')
            self.assertTrue('w/out StarsAccount: uid' in record.msg)
