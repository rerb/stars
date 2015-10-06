from django.test import TestCase
from django.test.client import Client
from file_cache_tag.templatetags import custom_caching
import django.core.cache as caches
from stars.apps.submissions.models import *


class FileCacheTest(TestCase):
    fixtures = ['silversubmissiontest.json']

    def setUp(self):
        self.client = Client()
        self.staff_client = Client()
        self.ss = SubmissionSet.objects.get(pk=349)
        self.url = self.ss.get_scorecard_url()

    def tearDown(self):
        pass

    def test_create_cache(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        filecache = caches.get_cache('filecache')
        self.assertTrue(filecache)
        key = custom_caching.generate_cache_key(self.url, [self.ss.id, False, "NO_EXPORT", False])
        cached_response = filecache.get(key)
        self.assertTrue(cached_response)

    def test_invalidate_cache(self):
        response = self.client.get(self.url)
        filecache = caches.get_cache('filecache')
        key = custom_caching.generate_cache_key(self.url, [self.ss.id, False, "NO_EXPORT", False])
        cached_response = filecache.get(key)
        custom_caching.invalidate_filecache(key)
        no_more_cache = filecache.get(key)
        self.assertTrue(cached_response)
        self.assertFalse(no_more_cache)

#    def test_invalidate_after_correction_approval(self):
#        response = self.client.get(self.url)
#        filecache = caches.get_cache('filecache')
#        key = custom_caching.generate_cache_key(self.url, [self.ss.id, False, "NO_EXPORT", False])
#        cached_response = filecache.get(key)
#        self.assertTrue(cached_response)
#
#        field = NumericSubmission.objects.get(pk=11999)
#
#        correction = DataCorrectionRequest(
#                                            date=datetime.now(),
#                                            reporting_field=field,
#                                            new_value=4,
#                                            explanation='just cuz',
#                                            approved=False)
#
#        correction.cache_invalidate()
#        response_after = filecache.get(key)
#        self.assertFalse(response_after)
