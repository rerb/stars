"""
    ExpiredRatingTest Unit Tests

    Test Premises:
     - confirm that the expire_ratings method handles expirations appropriately
"""
from django.test import TestCase
from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import SubmissionSet
from stars.apps.credits.models import Rating

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

        self.r = Rating.objects.create(name="Rating 1")
        self.i = Institution.objects.create(name="Inst 1")
        self.ss = SubmissionSet.objects.create(
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
