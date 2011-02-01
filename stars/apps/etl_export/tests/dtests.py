"""
    ETL Export Doctests
    
    Test Premises:
     - etl_export can create ETL entries
     - compare and replace changed entries
"""
   
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime, date

from stars.apps.institutions.models import Institution
from stars.apps.credits.models import CreditSet, Rating
from stars.apps.submissions.models import SubmissionSet
from stars.apps.etl_export.utils import *

class TestETL(TestCase):
#    fixtures = ['etl_tests.json']

    def setUp(self):
        pass 
    
    def testExport(self):
    
        date1 = date(year=2010, month=1, day=1)
        date2 = date(year=2010, month=2, day=2)
        
        i = Institution(
         aashe_id = 1,
         name = "test institution",
         contact_first_name = "first",
         contact_last_name = "last",
         contact_title = "title",
         contact_department = "dept",
         contact_phone = "800-5551212",
         contact_email = "test@example.com"
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
        
        u = User()
        u.save()
        
        ss = SubmissionSet(
         institution = i,
         creditset = cs,
         date_registered = date1,
         date_submitted = date1,
         date_reviewed = date1,
         submission_deadline = date1,
         registering_user = u,
         rating = r,
         status = 'r',
        )
        ss.save()
        
        ss2 = SubmissionSet(
         institution = i,
         creditset = cs2,
         date_registered = date2,
         date_submitted = date2,
         date_reviewed = date2,
         submission_deadline = date2,
         registering_user = u,
         rating = None,
         status = 'ps',
        )
        ss2.save()
        
        etl_a = populate_etl_entry(i)
        self.assertEqual(etl_a.liaison_first_name, 'first')
        self.assertEqual(etl_a.liaison_last_name, 'last')
        self.assertEqual(etl_a.liaison_title, 'title')
        self.assertEqual(etl_a.liaison_department, 'dept')
        self.assertEqual(etl_a.liaison_phone, '800-5551212')
        self.assertEqual(etl_a.liaison_email, 'test@example.com')
        self.assertEqual(etl_a.current_rating, 'gold')
        self.assertEqual(etl_a.participant_status, "Pending Submission")
        self.assertEqual(etl_a.registration_date, date(2010, 2, 2))
        
        etl_b = populate_etl_entry(i)
        self.assertEqual(etl_a, etl_b)
        self.assertFalse(etl_a != etl_b)
        
        ss2.status = 'pr'
        ss2.save()
        etl_c = populate_etl_entry(i)
        self.assertEqual(etl_c.participant_status, "Processing Submission")
        self.assertEqual(etl_a.participant_status, "Pending Submission")
        self.assertEqual(etl_b.registration_date, date(2010, 2, 2))
        self.assertTrue(etl_a != etl_c)
        
        result = update_etl_for_institution(i, None)
        self.assertTrue(result)
        
        etl_1 = ETL.objects.all()[0]
        result = update_etl_for_institution(i, etl_1)
        self.assertFalse(result)
        
        ss.status = 'pr'
        ss.save()
        
        etl_2 = ETL.objects.all()[0]
        result = update_etl_for_institution(i, etl_2)
        self.assertTrue(result)
        
        etl_to_del = populate_etl_entry(i)
        etl_to_del.aashe_id = 2
        etl_to_del.save()
        
        self.assertEqual(ETL.objects.count(), 2)
        update_etl()
        self.assertEqual(ETL.objects.count(), 1)
