"""
    Doctests for the subscription monitor task

    Test premises:

        - Expiration with renewal
        - Subscription Expirations
        - Rating Expirations

"""
from django.test import TestCase
from django.core import mail

from stars.apps.institutions.models import Institution, Subscription
from stars.apps.tasks.subscription_monitor import update_institution_properties

from datetime import date, timedelta


class SubscriptionMonitorTest(TestCase):
    fixtures = ['subscription_monitor_test.json',
                'notification_emailtemplate_tests.json']

    def setUp(self):
        pass

    def test_expiration(self):
        i = Institution.objects.get(pk=1)

        # new subscription
        sub = Subscription(institution=i,
                           start_date=date.today(),
                           end_date=date.today() + timedelta(days=365),
                           amount_due=0)
        sub.save()

        update_institution_properties()
        i = Institution.objects.get(pk=1)
        self.assertTrue(i.is_participant)
        self.assertEqual(i.current_subscription.id, sub.id)
        # no email sent
        self.assertTrue(len(mail.outbox) == 0)

        # expiration
        sub.start_date = date.today() - timedelta(days=365)
        sub.end_date = date.today() - timedelta(days=1)
        sub.save()

        update_institution_properties()
        i = Institution.objects.get(pk=1)
        self.assertFalse(i.is_participant)
        self.assertEqual(i.current_subscription, None)
        # send expiration email
        self.assertTrue(len(mail.outbox) == 1)

        # rollover
        i.is_participant = True
        i.save()
        sub = Subscription(institution=i,
                           start_date=date.today(),
                           end_date=date.today() + timedelta(days=365),
                           amount_due=0)
        sub.save()

        update_institution_properties()
        i = Institution.objects.get(pk=1)
        self.assertTrue(i.is_participant)
        self.assertEqual(i.current_subscription.id, sub.id)
        # no additional emails sent
        self.assertTrue(len(mail.outbox) == 1)
