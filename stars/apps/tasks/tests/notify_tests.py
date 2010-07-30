"""
    Doctests for the registration notification tool that will notify institutions
    that it has been over (4) weeks since they registered and haven't paid

    Test premises:
        - Ensure that `get_overdue_payments` returns the correct Submission Sets
"""
from django.test import TestCase
from django.core import mail

from stars.apps.tasks.notifications import *

from datetime import date
import sys

class NotificationTest(TestCase):
    fixtures = ['notification_test.json',]

    def setUp(self):
        pass

    def testOverdueList(self):
        """
            Tests:
                - Ensure that `get_overdue_payments` returns the correct SubmissionSets
                2011-05-01 2011-05-03
        """
        
        today = date(year=2010, month=5, day=29)
        ss_list = get_overdue_payments(today)
        self.assertTrue(len(ss_list) == 1)
        
        today = date(year=2010, month=5, day=31)
        ss_list = get_overdue_payments(today)
        self.assertTrue(len(ss_list) == 2)
        
        today = date(year=2010, month=5, day=25)
        ss_list = get_overdue_payments(today)
        self.assertTrue(len(ss_list) == 0)
        
    def test_overdue_notify(self):
        """
            http://docs.djangoproject.com/en/dev/topics/testing/#e-mail-services
            Tests:
                - Show that only unpaid institutions are notified
        """
        mail.outbox = []
        
        current_date = date(year=2010, month=5, day=25)
        send_overdue_notifications(current_date)
        self.assertTrue(len(mail.outbox) == 0)
        
        current_date = date(year=2010, month=5, day=29)
        send_overdue_notifications(current_date)
        self.assertTrue(len(mail.outbox) == 1)
        
        current_date = date(year=2010, month=5, day=31)
        send_overdue_notifications(current_date)
        # Only one more should be sent, because of the count limit on notifications
        self.assertTrue(len(mail.outbox) == 2)
        
    def test6MonthList(self):
        """
            Tests:
                - Ensure that `get_six_month_sets` returns the correct SubmissionSets
        """
        
        today = date(year=2010, month=1, day=30)
        ss_list = get_six_month_sets(today)
        self.assertTrue(len(ss_list) == 0)
        
        today = date(year=2010, month=10, day=30)
        ss_list = get_six_month_sets(today)
        self.assertTrue(len(ss_list) == 1)
        
        today = date(year=2010, month=11, day=1)
        ss_list = get_six_month_sets(today)
        self.assertTrue(len(ss_list) == 2)
        
        today = date(year=2010, month=11, day=3)
        ss_list = get_six_month_sets(today)
        self.assertTrue(len(ss_list) == 4)
        
        today = date(year=2010, month=7, day=31)
        ss_list = get_six_month_sets(today)
        self.assertTrue(len(ss_list) == 0)
        
    def test_6month_notify(self):
        """
            Tests:
                - Show that only unpaid institutions are notified
        """
        mail.outbox = []

        current_date = date(year=2010, month=1, day=30)
        send_six_month_notifications(current_date)
        self.assertTrue(len(mail.outbox) == 0)

        current_date = date(year=2010, month=10, day=30)
        send_six_month_notifications(current_date)
        self.assertTrue(len(mail.outbox) == 1)

        current_date = date(year=2010, month=11, day=1)
        send_six_month_notifications(current_date)
        # Only one more should be sent, because of the count limit on notifications
        self.assertTrue(len(mail.outbox) == 2)
        
    def test_send_notification(self):
        """
            Tests:
                - notifications only get sent `count` times (EmailNotification objects created)
                - email shows up in outbox
        """
        mail.outbox = []
        
        for i in range(0, 3):
            send_notification("tst", "test_1", ["ben@aashe.org"], "message", "subject", count=2)
        
        self.assertTrue(len(mail.outbox) == 2 )