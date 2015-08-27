"""
    ExpiredRatingTest Unit Tests

    Test Premises:
     - confirm that the expire_ratings method handles expirations appropriately
"""
from django.test import TestCase
from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import SubmissionSet
from stars.apps.credits.models import Rating
from stars.test_factories import SubmissionSetFactory, RatingFactory

import sys
from datetime import datetime, timedelta
from ..utils import expire_ratings


class ExpiredRatingTest(TestCase):
    """
        - rating hasn't expired: no action
        - rating has expired: cleared from institution, marked expired
        - rating has expired, but not current rating: mark expired
    """

    def setUp(self):
        """
            intitalize the test with an institution with a current submission
            that's just 10 days old
        """

        td = timedelta(days=10)
        new_time = datetime.today() - td

        self.i = Institution.objects.create(name="Inst 1")
        self.r = RatingFactory(name="Rating 1")
        self.ss = SubmissionSetFactory(
            creditset=self.r.creditset,
            institution=self.i,
            status="r",
            expired=False,
            date_submitted=new_time,
            rating=self.r
        )
        self.i.current_rating = self.r
        self.i.rated_submission = self.ss
        self.i.save()

    def testExpiration(self):
        """
            Intially, the institution shouldn't expire
        """
        # rating hasn't expired: no action
        expire_ratings()
        self.assertEqual(self.i.current_rating.id, self.r.id)

        # rating has expired: cleared from institution, marked expired
        td = timedelta(days=366*3)
        new_time = datetime.today() - td
        self.ss.date_submitted = new_time
        self.ss.save()
        expire_ratings()
        self.i = Institution.objects.all()[0]
        self.ss = SubmissionSet.objects.all()[0]
        self.assertEqual(self.i.rated_submission, None)
        self.assertEqual(self.i.current_rating, None)
        self.assertTrue(self.ss.expired)

        # rating has expired, but not current rating: mark expired
        td = timedelta(days=366*3)
        new_time = datetime.today() - td
        self.ss.date_submitted = new_time
        self.ss.expired = False
        self.ss.save()
        td = timedelta(days=365)
        new_time = datetime.today() - td
        new_ss = SubmissionSetFactory(
            creditset=self.r.creditset,
            institution=self.i,
            status="r",
            expired=False,
            date_submitted=new_time,
            rating=self.r
        )
        self.i.rated_submission = new_ss
        self.i.current_rating = self.r
        self.i.save()
        expire_ratings()
        self.i = Institution.objects.all()[0]
        self.ss = SubmissionSet.objects.all()[0]
        self.assertEqual(self.i.current_rating, self.r)
        self.assertEqual(self.i.rated_submission, new_ss)
        self.assertTrue(self.ss.expired)
