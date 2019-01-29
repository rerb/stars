from datetime import datetime
import os

import django.core.cache as caches
from django.core.exceptions import SuspiciousOperation
from django.core.management import call_command
from django.test import TestCase
from django.test.client import Client
from file_cache_tag.templatetags import custom_caching

from stars.apps.submissions.models import DataCorrectionRequest
from stars.test_factories.submissions_factories import (
        DocumentationFieldFactory,
        NumericDocumentationFieldSubmissionFactory
    )


class FileCacheTest(TestCase):

    def setUp(self):
        documentation_field = DocumentationFieldFactory(type='numeric')

        self.documentation_field_submission = (
            NumericDocumentationFieldSubmissionFactory(
                documentation_field=documentation_field,
                value=1))

        self.submissionset = (
            self.documentation_field_submission.get_submissionset())
        self.submissionset.status = "r"
        self.submissionset.date_submitted = '2016-01-19'
        preliminary_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "tool/my_submission/tests/test.pdf")
        self.submissionset.presidents_letter = preliminary_path[1:]
        self.submissionset.save()

        credit = documentation_field.credit
        credit.name = "Innovation"
        credit.acronym = "IN"
        credit.save()

        self.client = Client()
        self.staff_client = Client()
        self.url = self.submissionset.get_scorecard_url()

    def tearDown(self):
        pass

    def get_self_url(self):
        try:
            response = self.client.get(self.url)
        except SuspiciousOperation as exc:
            self.fail(exc)
        else:
            return response

    def test_create_cache(self):
        response = self.get_self_url()
        self.assertEqual(response.status_code, 200)
        filecache = caches.get_cache('filecache')
        self.assertTrue(filecache)
        key = custom_caching.generate_cache_key(
            self.url, [self.submissionset.id, False, "NO_EXPORT", False])
        cached_response = filecache.get(key)
        self.assertTrue(cached_response)

    def test_invalidate_cache(self):
        _ = self.get_self_url()  # noqa
        filecache = caches.get_cache('filecache')
        key = custom_caching.generate_cache_key(
            self.url, [self.submissionset.id, False, "NO_EXPORT", False])
        cached_response = filecache.get(key)
        custom_caching.invalidate_filecache(key)
        no_more_cache = filecache.get(key)
        self.assertTrue(cached_response)
        self.assertFalse(no_more_cache)

    def test_invalidate_after_correction_approval(self):
        _ = self.get_self_url()  # noqa
        filecache = caches.get_cache('filecache')
        key = custom_caching.generate_cache_key(
            self.url, [self.submissionset.id, False, "NO_EXPORT", False])
        cached_response = filecache.get(key)
        self.assertTrue(cached_response)

        correction = DataCorrectionRequest(
            date=datetime.now(),
            reporting_field=self.documentation_field_submission,
            new_value=4,
            explanation='just cuz',
            approved=False)

        correction.cache_invalidate()
        response_after = filecache.get(key)
        self.assertFalse(response_after)

    def test_invalidate_after_manual_edit(self):
        _ = self.get_self_url()  # noqa
        filecache = caches.get_cache('filecache')
        key = custom_caching.generate_cache_key(
            self.url, [self.submissionset.id, False, "NO_EXPORT", False])
        cached_response = filecache.get(key)
        self.assertTrue(cached_response)
        self.submissionset.save()
        no_cache = filecache.get(key)
        self.assertFalse(no_cache)

    def test_managament_invalidation(self):
        url = 'https://reports.aashe.org' + self.url
        _ = self.get_self_url()  # noqa
        filecache = caches.get_cache('filecache')
        key = custom_caching.generate_cache_key(
            self.url, [self.submissionset.id, False, "NO_EXPORT", False])
        cached_response = filecache.get(key)
        self.assertTrue(cached_response)
        call_command('clear_cache', url)
        no_cache = filecache.get(key)
        self.assertFalse(no_cache)
