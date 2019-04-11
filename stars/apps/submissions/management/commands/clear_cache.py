#!/usr/bin/env python
"""
    Clears file-bsed cache for provided URL
"""

from django.core.management.base import BaseCommand
from stars.apps.submissions.models import (SubmissionSet,
                                           generate_cache_key,
                                           invalidate_filecache)
from stars.apps.institutions.models import Institution


class Command(BaseCommand):

    args = '<url>'

    def handle(self, *args, **options):
        clear_cache(args[0])


def clear_cache(url):

    # Extract submission set data from URL
    pieces = url.split('/')
    date_submitted = pieces[6]
    slug = pieces[4]
    institution = Institution.objects.get(slug=slug)

    ss = SubmissionSet.objects.get(
        institution=institution, date_submitted=date_submitted, status="r")
    ss.invalidate_cache()
