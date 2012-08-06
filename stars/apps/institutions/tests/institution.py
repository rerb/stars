"""Tests for apps.institutions.models.Institution.
"""
from unittest import TestCase

import testfixtures

from stars.apps.institutions.models import Institution


class InstitutionTest(TestCase):

    def test_update_from_iss_logging(self):
        """Does update_from_iss log an error if there's no ISS instituion?
        """
        minstitution = MockInstitution()
        minstitution.name = 'bob'

        with testfixtures.LogCapture('stars') as log:
            minstitution.update_from_iss()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].module_path.startswith('stars'))
        self.assertTrue('No ISS institution found bob' in log.records[0].msg)

    def test_profile_logging(self):
        """Does profile log an error if there's no Organization?
        """
        institution = Institution()
        institution.aashe_id = '-99999'

        with testfixtures.LogCapture('stars') as log:
            institution.profile

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].module_path.startswith('stars'))
        self.assertTrue(
            'No ISS institution found for aashe_id' in log.records[0].msg)

    def test_set_slug_from_iss_institution_logging(self):
        """Does set_slug_from_iss_institution log exceptions (as errors)?
        """
        minstitution = MockInstitution()

        with testfixtures.LogCapture('stars') as log:
            minstitution.set_slug_from_iss_institution(-99999)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].module_path.startswith('stars'))
        self.assertTrue('profile relationship error' in log.records[0].msg)


class MockInstitution(Institution):
    """Overrides Institution.profile, which can log errors.
    """

    @property
    def profile(self):
        return False
