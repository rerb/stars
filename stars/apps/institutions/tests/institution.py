"""Tests for apps.institutions.models.Institution.
"""
from unittest import TestCase

import testfixtures

from stars.apps.institutions.models import Institution
from stars.test_factories import InstitutionFactory


class InstitutionTest(TestCase):

    def test_update_from_iss_logging(self):
        """Does update_from_iss log an error if there's no ISS instituion?
        """
        institution = Institution()
        institution.name = 'bob'

        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.institutions.models.Institution.profile',
                          None)
                institution.update_from_iss()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
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
        self.assertTrue(
            'No ISS institution found for aashe_id' in log.records[0].msg)

    def test_set_slug_from_iss_institution_logging(self):
        """Does set_slug_from_iss_institution log exceptions (as errors)?
        """
        institution = Institution()

        def raiser(*args):
            raise Exception('bo-o-o-gus exception')

        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.institutions.models.Institution.profile',
                          MockProfile())
                r.replace('stars.apps.institutions.models.slugify',
                          raiser)
                institution.set_slug_from_iss_institution(-99999)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue('profile relationship error' in log.records[0].msg)

    def test_get_location_string_no_city(self):
        """Does get_location_string() work when there's no city?"""
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.profile',
                      MockProfile(city='', state='ST', country_iso='CO'))
            institution = InstitutionFactory()
            self.assertEqual(institution.get_location_string(),
                             'ST, CO')


    def test_get_location_string_no_state(self):
        """Does get_location_string() work when there's no state?"""
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.profile',
                      MockProfile(city='CITY', state='', country_iso='CO'))
            institution = InstitutionFactory()
            self.assertEqual(institution.get_location_string(),
                             'CITY, CO')


    def test_get_location_string_no_country(self):
        """Does get_location_string() work when there's no country?"""
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.profile',
                      MockProfile(city='CITY', state='ST', country_iso=''))
            institution = InstitutionFactory()
            self.assertEqual(institution.get_location_string(),
                             'CITY, ST')


    def test_get_location_string_no_city_no_country(self):
        """Does get_location_string() work when there's no city or country?"""
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.profile',
                      MockProfile(city='', state='ST', country_iso=''))
            institution = InstitutionFactory()
            self.assertEqual(institution.get_location_string(),
                             'ST')


    def test_get_location_string_no_nothing(self):
        """Does get_location_string() work if there's no city, state or country?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.profile',
                      MockProfile(city='', state='', country_iso=''))
            institution = InstitutionFactory()
            self.assertEqual(institution.get_location_string(),
                             '')


class MockProfile(object):

    def __init__(self, state='', city='', country_iso=''):
        self.org_name = 'MockProfile Org Name'
        self.state = state
        self.city = city
        self.country_iso = country_iso
