"""
    Submission Mixin Tests
"""
from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import TestCase

from stars.apps.accounts.mixins import SubmissionMixin
from stars.apps.institutions.models import StarsAccount, Institution
from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import SubmissionSet, Payment
from dummy_request import DummyRequest


# Define a custom `BaseClass` for use with the mixin
class BaseClass(object):
    def __call__(self, request, *args, **kwargs):
        return "Hello World!"


class SubClass(SubmissionMixin, BaseClass):
    pass


class SubmissionMixinTest(TestCase):

    def setUp(self):
        self.i = Institution(name='Fake Institution', aashe_id='-11',
                             enabled=True)
        self.i.save()
        self.cs = CreditSet(version='100', release_date=datetime.now(),
                            tier_2_points='.25', is_locked=False)
        self.cs.save()
        self.u = User.objects.create_user('s_testuser', 'test@example.com',
                                          'testpw')
        self.u.current_inst = self.i
        self.u.account_list = []
        self.u.save()
        self.account = StarsAccount(institution=self.i, terms_of_service=True,
                                    user_level='admin', user=self.u)
        self.account.save()
        self.u.account = self.account
        self.u.save()
        self.ss = SubmissionSet(creditset=self.cs, institution=self.i,
                                date_registered=datetime.now(),
                                registering_user=self.u)
        self.ss.is_visible = True
        self.ss.save()

        self.p = Payment(submissionset=self.ss, type='check',
                         date=datetime.now(),
                         amount='0', user=self.u)
        self.p.save()

        self.request = DummyRequest(self.u)
        self.sc = SubClass()

    def test_active_submission_exists(self):
        """Is this a test of this test setup?"""
        self.assertEqual(self.sc(self.request), 'Hello World!')

    def test_no_active_submission_so_redirect(self):
        self.u.is_staff = True
        self.u.save()
        self.i.current_submission = None
        self.i.save()
        self.assertIsInstance(self.sc(self.request), HttpResponseRedirect)

    def test_active_submission_is_disabled_so_raise_permissiondenied(self):
        self.i.current_submission = self.ss
        self.i.save()
        self.ss.is_visible = False  # causes is_enabled() to be False
        self.ss.save()
        self.assertFalse(self.ss.is_enabled())
        with self.assertRaises(Exception) as e:
            self.sc(self.request)
        self.assertEqual(e.__class__.__name__, 'PermissionDenied')

    def test_user_is_just_an_admin_so_redirect(self):
        self.u.is_staff = False
        self.u.save()
        self.i.current_submission = self.ss
        self.i.save()
        self.assertIsInstance(self.sc(self.request), HttpResponseRedirect)

    def test_user_can_only_submit_so_permission_is_denied(self):
        self.account.user_level = 'submit'
        self.account.save()
        with self.assertRaises(Exception) as e:
            self.sc(self.request)
        self.assertEqual(e.__class__.__name__, 'PermissionDenied')
