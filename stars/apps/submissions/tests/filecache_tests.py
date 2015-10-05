from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from file_cache_tag.templatetags import custom_caching
from stars.test_factories.submissions_factories import SubmissionSetFactory, CreditUserSubmissionFactory,\
    NumericDocumentationFieldSubmissionFactory
import django.core.cache as caches
from stars.apps.submissions.models import *


class FileCacheTest(TestCase):
    fixtures = ['data_correction_test.json', 'notification_emailtemplate_tests.json']

    def setUp(self):
        self.client = Client()
        self.staff_client = Client()
        SubmissionSetFactory()
        CreditUserSubmissionFactory()
        NumericDocumentationFieldSubmissionFactory()
        self.ss = SubmissionSet.objects.get(pk=1)
        self.cus = CreditUserSubmission.objects.get(pk=1)
        self.field = NumericSubmission.objects.get(pk=1)
        print self.cus
        self.url = '/institutions/' + self.ss.institution.slug + '/report/' + str(self.ss.id) + '/'

    def tearDown(self):
        pass

    def test_load_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
