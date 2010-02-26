import unittest
from datetime import date

from stars.apps.registration.views import init_submissionset
from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import PAYMENT_TYPE_CHOICES

from django.contrib.auth.models import User

class RegistrationTestCase(unittest.TestCase):
    """
        Tests:
        
    """
    def setUp(self):
        self.user = User.objects.create(username='tester__aashe_org', is_active=True)
        self.user.save()
        self.inst = Institution.objects.create( name='Test Institution',
                                                aashe_id=-1,
                                                contact_first_name='Test',
                                                )
        self.inst.save()

    def test_init_submissionset(self):
        """
            Tests:
                init_submissionset(institution, user)
            (I might make this a doctest later...)
        """

        today = date(2010, 2, 26)
        one_year_hence = date(2011, 2, 26)
        submissionset = init_submissionset(self.inst, self.user, today)
        
        self.assertEquals(submissionset.status, 'ps')
        self.assertEquals(submissionset.date_registered, today)
        self.assertEquals(submissionset.submission_deadline, one_year_hence)
        self.assertEquals(submissionset.registering_user, self.user)
        
        # leap year case
        today = date(2012, 2, 26)
        one_year_hence = date(2013, 2, 25)
        submissionset.delete()
        submissionset = init_submissionset(self.inst, self.user, today)
        
        self.assertEquals(submissionset.submission_deadline, one_year_hence)