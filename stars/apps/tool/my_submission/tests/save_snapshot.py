"""
    Tests that a snapshot is saved successfully
"""
import tempfile

from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.conf import settings

from stars.apps.submissions.models import SubmissionSet
from stars.apps.institutions.models import Institution


class SaveSnapshot(TestCase):

    fixtures = ['submit_for_rating_tests.json',
                'notification_emailtemplate_tests.json']

    def setUp(self):

        print " Testing submission for rating"

        settings.CELERY_ALWAYS_EAGER = True

        self.ss = SubmissionSet.objects.get(pk=1)
        self.ss.save()

        self.inst_slug = 'test-institution'
        self.url = "/tool/%s/submission/1/snapshot/" % self.inst_slug

    def test_snapshot(self):

        print " - testing snapshot creation"
        self.assertEqual(SubmissionSet.objects.filter(status='f').count(), 0)
        
        c = Client()
        c.login(username='test_user', password='test')
        response = c.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(SubmissionSet.objects.filter(status='f').count(), 1)