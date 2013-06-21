"""
    Send one reminder immediately after a subscription expires
    and then another 60 days later (30 days before the discount expires)
"""

from django.test import TestCase
from django.core import mail

from stars.apps.tasks.notifications import send_renewal_reminder

from datetime import date


class RenewNotifyTest(TestCase):
    fixtures = ['renew_notify_test.json',
                'notification_emailtemplate_tests.json']

    def setUp(self):
        pass

    def test_30_day_notification(self):
        """
            Tests: send_renewal_reminder()

             subscription dates in fixture:
                I1:  2010-04-15 to 2011-04-15
        """

        print "TESTING 30 Day Discount Renewal Reminder"

        mail.outbox = []

        # don't send the email after the deadline
        current_date = date(year=2011, month=7, day=14)
        td = current_date - date(year=2011, month=4, day=15)
        print "TIME DELTA: %d" % td.days
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 0)

        # before 60 days 2011-6-14 don't send emails
        current_date = date(year=2011, month=6, day=13)
        td = current_date - date(year=2011, month=4, day=15)
        print "TIME DELTA: %d" % td.days
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 0)

        # after 60 days 2011-6-14 send email
        current_date = date(year=2011, month=6, day=14)
        td = current_date - date(year=2011, month=4, day=15)
        print "TIME DELTA: %d" % td.days
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 1)

        # don't send any more
        current_date = date(year=2011, month=6, day=15)
        td = current_date - date(year=2011, month=4, day=15)
        print "TIME DELTA: %d" % td.days
        send_renewal_reminder(current_date)
        self.assertTrue(len(mail.outbox) == 1)
