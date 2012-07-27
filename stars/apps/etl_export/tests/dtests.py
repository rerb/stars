"""
    etl_export.models.Institution Export Doctests

    Test Premises:
     - etl_export can create etl_export.models.Institution entries
     - compare and replace changed entries
"""

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date

from stars.apps import institutions
from stars.apps.credits.models import CreditSet, Rating
from stars.apps import submissions
from stars.apps.etl_export.utils import *
from stars.apps import etl_export

class TestETL(TestCase):
#    fixtures = ['etl_tests.json']

    def setUp(self):
        pass

    def testExport(self):

        date1 = date(year=2010, month=1, day=1)
        date2 = date(year=2010, month=2, day=2)

        i = institutions.models.Institution(
         aashe_id = 1,
         name = "test institution",
         contact_first_name = "first",
         contact_last_name = "last",
         contact_title = "title",
         contact_department = "dept",
         contact_phone = "800-5551212",
         contact_email = "test@example.com",
         )
        i.save()

        cs = CreditSet(
         version = 'test',
         release_date = date1,
         tier_2_points = 0.25,
         is_locked = True,
         scoring_method = 'get_STARS_v1_0_score',
        )
        cs.save()

        cs2 = CreditSet(
         version = 'test2',
         release_date = date1,
         tier_2_points = 0.25,
         is_locked = True,
         scoring_method = 'get_STARS_v1_0_score',
        )
        cs2.save()

        r = Rating(
         name = 'gold',
         minimal_score = 0,
         creditset = cs
        )
        r.save()

        i.current_rating = r
        i.save()

        u = User()
        u.save()

        ss = submissions.models.SubmissionSet(
         institution = i,
         creditset = cs,
         date_registered = date1,
         date_submitted = date1,
         date_reviewed = date1,
         registering_user = u,
         rating = r,
         status = 'r',
        )
        ss.save()

        i.set_active_submission(ss)

        ss2 = submissions.models.SubmissionSet(
         institution = i,
         creditset = cs2,
         date_registered = date2,
         date_submitted = date2,
         date_reviewed = date2,
         registering_user = u,
         rating = None,
         status = 'ps',
        )
        ss2.save()

        i_state = institutions.models.InstitutionState(
            institution = i,
            active_submission_set = ss2,
            latest_rated_submission_set = ss
            )
        i_state.save()

        # Confirm is_active is populating properly

        # @BEN - etl_export.models.SubmissionSet has a boolean is_active
        # attribute, but submissions.models.SubmissionSet doesn't;
        # delete this bit of the test or compare is_active to a different
        # value, like is_enabled()?
        etl_ss = etl_export.models.SubmissionSet()
        etl_ss.populate(ss)
        self.assertFalse(etl_ss.is_active)

        etl_ss2 = etl_export.models.SubmissionSet()
        etl_ss2.populate(ss2)
        # self.assertTrue(etl_ss2.is_active)

        etl_a = etl_export.models.Institution()
        etl_a.populate(i)
        self.assertEqual(etl_a.liaison_first_name, 'first')
        self.assertEqual(etl_a.liaison_last_name, 'last')
        self.assertEqual(etl_a.liaison_title, 'title')
        self.assertEqual(etl_a.liaison_department, 'dept')
        self.assertEqual(etl_a.liaison_phone, '800-5551212')
        self.assertEqual(etl_a.liaison_email, 'test@example.com')

        self.assertEqual(etl_a.current_rating, 'gold')

        # @BEN - neither Institution in etl_export.models nor
        # institutions.models has a participant_status attribute;
        # delete this assertion or compare different attributes?
        # self.assertEqual(etl_a.participant_status, "Pending Submission")

        # @BEN - etl_export.models.Institution has a registration_date
        # attribute, but institutions.models.Institution doesn't;
        # delete this assertion or compare to a different value?
        # self.assertEqual(etl_a.registration_date, date(2010, 2, 2))

        etl_b = etl_export.models.Institution()
        etl_b.populate(i)
        self.assertFalse(etl_a.etl_has_changed(etl_b))

        ss2.status = 'pr'
        ss2.save()
        etl_c = etl_export.models.Institution()
        etl_c.populate(i)
        # more checking of etl_export.models.Institution.participant_status,
        # and registration_date, which don't exist:
        # self.assertEqual(etl_c.participant_status, "Processing Submission")
        # self.assertEqual(etl_a.participant_status, "Pending Submission")
        # self.assertEqual(etl_b.registration_date, date(2010, 2, 2))
        # self.assertTrue(etl_a.etl_has_changed(etl_c))

        # Add the first etl_export.models.Institution object
        etl_1 = etl_export.models.Institution()
        etl_1.populate(i)
        etl_1.save()

        # Update the export, but there were no changes
        etl_2 = etl_export.models.Institution()
        etl_2.populate(i)
        result = etl_1.etl_update(etl_2)
        self.assertFalse(result)

        # @BEN - looks like this bit is checking if changes are
        # propagated correctly, by changing the status on the SubmisionSet
        # associated with i, making a new etl_export.Institution from i,
        # then comparing it to the etl_export.Institution created from
        # i before the status on the SubmissionSet was changed.  Should
        # the status of a SubmissionSet be reflected in the etl_export.
        # Institution?  Doesn't look like it is.

        # ss.status = 'pr'
        # ss.save()

        # # Update again, but this time with changes
        # new_etl = etl_export.models.Institution()
        # new_etl.populate(i)
        # result = etl_1.etl_update(new_etl)
        # self.assertTrue(result)

        # Now make sure it deletes an object when it doesn't exist
        etl_to_del = etl_export.models.Institution()
        etl_to_del.populate(i)
        etl_to_del.id = 2
        etl_to_del.save()

        self.assertEqual(etl_export.models.Institution.objects.count(), 2)
        etl_export.models.Institution.etl_run_update()
        self.assertEqual(etl_export.models.Institution.objects.count(), 1)
