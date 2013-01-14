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

        i.set_active_submission(ss2)

        i_state = institutions.models.InstitutionState(
            institution = i,
            active_submission_set = ss2,
            latest_rated_submission_set = ss
            )
        i_state.save()

        # Confirm is_active is populating properly
        etl_ss = etl_export.models.SubmissionSet()
        etl_ss.populate(ss)
        self.assertFalse(etl_ss.is_active)

        etl_ss2 = etl_export.models.SubmissionSet()
        etl_ss2.populate(ss2)
        self.assertTrue(etl_ss2.is_active)

        etl_a = etl_export.models.Institution()
        etl_a.populate(i)
        self.assertEqual(etl_a.liaison_first_name, 'first')
        self.assertEqual(etl_a.liaison_last_name, 'last')
        self.assertEqual(etl_a.liaison_title, 'title')
        self.assertEqual(etl_a.liaison_department, 'dept')
        self.assertEqual(etl_a.liaison_phone, '800-5551212')
        self.assertEqual(etl_a.liaison_email, 'test@example.com')

        self.assertEqual(etl_a.current_rating, 'gold')

        self.assertEqual(etl_a.is_participant, i.is_participant)

        etl_b = etl_export.models.Institution()
        etl_b.populate(i)
        self.assertFalse(etl_a.etl_has_changed(etl_b))

        ss2.status = 'pr'
        ss2.save()
        etl_c = etl_export.models.Institution()
        etl_c.populate(i)

        # Add the first etl_export.models.Institution object
        etl_1 = etl_export.models.Institution()
        etl_1.populate(i)
        etl_1.save()

        # Update the export, but there were no changes
        etl_2 = etl_export.models.Institution()
        etl_2.populate(i)
        result = etl_1.etl_update(etl_2)
        self.assertFalse(result)

        # Update again, but this time with changes
        i.is_participant = not i.is_participant
        i.save()
        new_etl = etl_export.models.Institution()
        new_etl.populate(i)
        result = etl_1.etl_update(new_etl)
        self.assertTrue(result)

        # Now make sure it deletes an object when it doesn't exist
        etl_to_del = etl_export.models.Institution()
        etl_to_del.populate(i)
        etl_to_del.id = 2
        etl_to_del.save()

        self.assertEqual(etl_export.models.Institution.objects.count(), 2)
        etl_export.models.Institution.etl_run_update()
        self.assertEqual(etl_export.models.Institution.objects.count(), 1)
