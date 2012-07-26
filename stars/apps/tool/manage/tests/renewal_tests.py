"""
    Unittests for the submission renewal process
"""
from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.conf import settings
from django.contrib.auth.models import User

from datetime import date
import sys, os, random

from stars.apps.tool.manage.views import _gets_discount
from stars.apps.submissions.models import SubmissionSet, NumericSubmission, Payment
from stars.apps.tasks.update_from_iss import run_update

class RenewalTest(TestCase):
    fixtures = ['submission_migration_test.json', 'notification_emailtemplate_tests.json', 'iss_testdata.json']
    multi_db = True

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        run_update()

    def test_gets_discount(self):
        """
        Given a subscription that ended on 1/31/11 ...
        """
        ss = SubmissionSet.objects.get(pk=1)
        i = ss.institution

        # If the current date is 3/1/11 (less than 90 days after 1/31/11):
        current_date = date(year=2011, month=3, day=1)

        # unsubmitted - gets discount
        self.assertTrue(_gets_discount(i, current_date))

        # date submitted before current_date - gets discount
        ss.status = 'r'
        ss.date_submitted = date(year=2011, month=2, day=1)
        ss.save()
        self.assertTrue(_gets_discount(i, current_date))

        # If the current date is 5/14/11:
        current_date = date(year=2011, month=5, day=14)

        # no discount for you
        self.assertFalse(_gets_discount(i, current_date))

        # If the current date is 5/1/11:
        current_date = date(year=2011, month=5, day=1)

        # date submitted 30 days before current date - gets discount
        ss.date_submitted = date(year=2011, month=4, day=1)
        ss.save()
        self.assertTrue(_gets_discount(i, current_date))

        # date submitted 100 days before current date - gets discount
        ss.date_submitted = date(year=2011, month=1, day=1)
        ss.save()
        self.assertTrue(_gets_discount(i, current_date))

        # unsubmitted 30 days before current date - gets discount
        ss.status = 'ps'
        ss.date_submitted = None
        ss.save()
        self.assertTrue(_gets_discount(i, current_date))

    def test_purchase_submission(self):
        """
            purchase_submissionset()

            Page loads
            - 200 response code

            Pay Later
            - results in a new submission
            - sends an email

            Pay w/ CC
            - transaction processes
            - results in a new submission
            - sends an email
        """
        import pdb; pdb.set_trace()

        user = User.objects.get(pk=1)
        user.set_password('test')
        user.save()

        c = Client()
        login = c.login(username='tester', password='test')
        self.assertTrue(login)

        # Total Submissions
        self.assertEqual(SubmissionSet.objects.count(), 1)

        url = "/tool/manage/submissionsets/purchase/"

        # Page Loads
        response = c.get(url)
        self.assertTrue(response.status_code == 200)

        # Pay Later
        post_dict = {'confirm': u'on',}
        response = c.post(url, post_dict)
        self.assertTrue(response.status_code == 302)

        # check payment
        p = Payment.objects.all().order_by('-date')[0]
        self.assertEqual(p.reason, "member_reg")

        self.assertEqual(SubmissionSet.objects.count(), 2)
        self.assertTrue(len(mail.outbox) == 2)

        # confirm the data migration
        self.assertEqual(NumericSubmission.objects.count(), 2)
        ns1 = NumericSubmission.objects.all()[0]
        ns2 = NumericSubmission.objects.all()[1]
        self.assertEqual(ns1.value, ns2.value)

       # print >> sys.stdout, mail.outbox[1].message()

        # # Pay Now
        # post_dict = {
        #                'name_on_card': 'Test Person',
        #                'card_number': '4007000000027',
        #                # 'card_number': '4222222222222',
        #                'exp_month': str(date.today().month),
        #                'exp_year': str(date.today().year + 1),
        #                'cv_code': '123',
        #                'billing_address': '123 Street rd',
        #                'billing_city': "City",
        #                'billing_state': 'RI',
        #                'billing_zipcode': '01234',
        #             }
        # response = c.post(url, post_dict)
        # self.assertTrue(response.status_code == 302)
        #
        # self.assertTrue(SubmissionSet.objects.count() == 3)
        # self.assertTrue(len(mail.outbox) == 4)
