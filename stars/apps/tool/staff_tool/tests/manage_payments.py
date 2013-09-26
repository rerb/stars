"""Tests for stars.apps.tool.staff_tool.views.
"""
from django.test import TestCase
from django.test.client import Client
from django.contrib.admin.models import User

from stars.apps.institutions.models import Subscription


class PaymentsTest(TestCase):

    fixtures = ['subscription_payment_testdata']

    def setUp(self):
        pass

    def test_add_payment(self):
        """
            Make sure that adding payment updates the amount_due
            and paid_in_full fields
        """
        c = Client()
        c.login(username='test_user', password='test')

        url = "/tool/test-institution/manage/payments/"
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        url = "/tool/admin/payments/test-institution/1/add/"
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        post_dict = {
                     "date": "2013-1-1",
                     "amount": "450",
                     "user": "5215",
                     "method": "check",
                     "confirmation": "123"
                     }
        response = c.post(url, post_dict)
        self.assertEqual(response.status_code, 302)

        s = Subscription.objects.get(pk=1)
        self.assertTrue(s.paid_in_full)
