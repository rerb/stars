from django.test import TestCase
from django.test.client import Client
from file_cache_tag.templatetags import custom_caching
import django.core.cache as caches
from stars.apps.submissions.models import *
from stars.test_factories.submissions_factories import (
        DocumentationFieldFactory,
        NumericDocumentationFieldSubmissionFactory
    )


class FileCacheTest(TestCase):

    def setUp(self):
        self.documentation_field = DocumentationFieldFactory(type='numeric')
        self.credit_submission = NumericDocumentationFieldSubmissionFactory(
            documentation_field=self.documentation_field,
            value=1
        )
        self.ss = self.credit_submission.get_submissionset()
        self.ss.status = "r"
        self.ss.presidents_letter = os.path.join(os.path.dirname(__file__), "..", "..", "tool/my_submission/tests/test.pdf")
        self.ss.save()
        self.c = self.documentation_field.credit
        self.c.name = "Innovation"
        self.c.acronym = "IN"
        self.c.save()
        self.client = Client()
        self.staff_client = Client()
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

    def test_invalidate_after_correction_approval(self):
        response = self.client.get(self.url)
        filecache = caches.get_cache('filecache')
        key = custom_caching.generate_cache_key(self.url, [self.ss.id, False, "NO_EXPORT", False])
        cached_response = filecache.get(key)
        self.assertTrue(cached_response)

        correction = DataCorrectionRequest(
                                            date=datetime.now(),
                                            reporting_field=self.credit_submission,
                                            new_value=4,
                                            explanation='just cuz',
                                            approved=False)

        correction.cache_invalidate()
        response_after = filecache.get(key)
        self.assertFalse(response_after)

    def test_invalidate_after_manual_edit(self):
        response = self.client.get(self.url)
        filecache = caches.get_cache('filecache')
        key = custom_caching.generate_cache_key(self.url, [self.ss.id, False, "NO_EXPORT", False])
        cached_response = filecache.get(key)
        self.assertTrue(cached_response)
        print "SAVE TIME!"
        self.ss.save()
        no_cache = filecache.get(key)
        self.assertFalse(no_cache)
