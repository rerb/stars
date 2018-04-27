"""Tests for apps.institutions.models.Institution.
"""
from unittest import TestCase

import testfixtures

from stars.apps.institutions.models import (REVIEW_SUBMISSION_STATUS,
                                            Institution,
                                            Subscription)
from stars.test_factories import InstitutionFactory, SubmissionSetFactory


class InstitutionTest(TestCase):

    def test_update_from_iss_logging(self):
        """Does update_from_iss log a warning if there's no ISS instituion?
        """
        institution = Institution()
        institution.name = 'bob'

        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.institutions.models.Institution.profile',
                          None)
                institution.update_from_iss()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'WARNING')
        self.assertTrue('No ISS institution found bob' in log.records[0].msg)

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

    def test_is_participant_in_review_mode(self):
        """When a submission is in review mode, is is_particpant True?
        """
        institution = InstitutionFactory()
        self.assertFalse(institution.is_participant)
        institution.current_submission = SubmissionSetFactory(
            status=REVIEW_SUBMISSION_STATUS)
        institution.save()
        self.assertTrue(institution.is_participant)

    def test_access_level_in_review_mode(self):
        """When a submission is in review mode, is access_level correct?
        """
        institution = InstitutionFactory()
        self.assertEqual(institution.access_level, Subscription.BASIC_ACCESS)
        institution.current_submission = SubmissionSetFactory(
            status=REVIEW_SUBMISSION_STATUS)
        institution.save()
        self.assertEqual(institution.access_level, Subscription.FULL_ACCESS)


class MockProfile(object):

    def __init__(self, state='', city='', country_iso=''):
        self.org_name = 'MockProfile Org Name'
        self.state = state
        self.city = city
        self.country_iso = country_iso
