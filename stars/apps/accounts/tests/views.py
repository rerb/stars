"""Tests for stars.apps.tool.manage.views.
"""
from unittest import TestCase

# from django.contrib.auth.models import User
import testfixtures

# from dummy_request import DummyRequest
# from stars.apps.institutions.models import Institution
from stars.apps.accounts import views

def mock_user_is_inst_admin(func, *args, **kwargs):
    return func(*args, **kwargs)


class ViewsTest(TestCase):

    def test_delete_account_logging(self):
        """Does delete_account log a message when an account is deleted?
        """
        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace(
                    'stars.apps.tool.manage.views.user_is_inst_admin',
                    mock_user_is_inst_admin)

                views.select_school(self.request, 999999)

        self.assertEqual(len(log.records), 1)
        for record in log.records:
            self.assertEqual(record.levelname, 'INFO')
            self.assertTrue(record.module_path.startswith('stars'))
            self.assertTrue('non-existent institution' in record.msg)
