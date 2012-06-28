from django.test import TestCase

from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import SubmissionSet

class FixturesTest(TestCase):
    fixtures = ['test_api_creditset.json', 'test_api_submissionset.json']

    def setUp(self):
        pass

    def testCreditSetLoad(self):
        self.assertTrue(CreditSet.objects.all() > 0)

    def testSubmisisonSetLoad(self):
        self.assertTrue(SubmissionSet.objects.all() > 0)
