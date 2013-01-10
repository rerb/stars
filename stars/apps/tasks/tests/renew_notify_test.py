"""
    Doctests for the registration notification tool that will notify institutions
    that it has been over (4) weeks since they registered and haven't paid

    Test premises:
        - Ensure that `get_overdue_payments` returns the correct Submission Sets
"""
from django.test import TestCase
from django.core import mail

from stars.apps.tasks.notifications import send_renewal_reminder

from datetime import date
import sys, os

class RenewNotifyTest(TestCase):
    fixtures = ['renew_notify_test.json', 'notification_emailtemplate_tests.json']

    def setUp(self):
        pass
        
    def test_renewal_notifications(self):
        """
            Tests: send_renewal_reminder()
            
            SubmissionSet submission dates in fixture:
                null
                2011-1-10
                2011-3-1
                2011-5-1
        """
        mail.outbox = []

        # before 4/1 don't send emails
        current_date = date(year=2011, month=3, day=30)
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 0)

        # after 4/1 there should only be one
        current_date = date(year=2011, month=4, day=2)
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 1)
        
        # still don't send
        current_date = date(year=2011, month=4, day=10)
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 1)
        
        current_date = date(year=2011, month=5, day=10)
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 2)
        
        current_date = date(year=2011, month=6, day=10)
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 2)
        
        current_date = date(year=2011, month=7, day=10)
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 3)
        
        # don't send any more
        current_date = date(year=2011, month=8, day=10)
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 3)
        
