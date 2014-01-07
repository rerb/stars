"""Tests for apps.submissions.models.SubmissionSet.
"""
from django.test import TestCase
import testfixtures

from stars.apps.credits.models import CreditSet, Rating
from stars.apps.institutions.models import (BASIC_ACCESS,
                                            FULL_ACCESS,
                                            Institution)
from stars.apps.submissions.models import SubmissionSet


class SubmissionSetTest(TestCase):

    fixtures = ['silversubmissiontest.json']

    def test_get_STARS_score_logging(self):
        """Does get_STARS_score log an error when there's no scoring method?
        """
        creditset = CreditSet()
        creditset.scoring_method = 'bogus_scoring_method'
        submissionset = SubmissionSet()
        submissionset.status = 'x'
        submissionset.creditset = creditset
        with testfixtures.LogCapture('stars') as log:
            submissionset.get_STARS_score()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith('No method'))

    def test_silver_score_gets_silver_rating(self):
        """If SubmissionSet has silver score, does it get silver rating?"""
        institution = Institution.objects.get(name__startswith='Agnes')
        institution.access_level = FULL_ACCESS
        institution.save()
        ss = SubmissionSet.objects.get(institution=institution)
        silver_rating = Rating.objects.get(creditset=ss.creditset,
                                           name='Silver')
        rating = ss.get_STARS_rating()
        self.assertEqual(rating, silver_rating)

    def test_basic_access_silver_score_keeps_silver_rating(self):
        """If BA SubmissionSet has silver score, does it keep silver rating?
        """
        institution = Institution.objects.get(name__startswith='Agnes')
        institution.access_level = BASIC_ACCESS
        institution.save()
        ss = SubmissionSet.objects.get(institution=institution)
        reporter_rating = Rating.objects.get(creditset=ss.creditset,
                                             name='Silver')
        rating = ss.get_STARS_rating()
        self.assertEqual(rating, reporter_rating)
