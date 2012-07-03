"""
Tests for institutions API.

These test cases fail if run via 'manage.py test' because the test
database has no data in it, and no fixtures are defined here.  They'll
run from the REPL as doctests, if you do this:

    import stars.apps.institutions.api.test as t
    import doctest
    doctest.testmod(t)
"""
import json

from stars.apps.api.test import StarsApiTestCase


class InstitutionResourceTestCase(StarsApiTestCase):

    list_path = '/api/v1/institutions/'
    detail_path = list_path + '24/'

    def test_get_institutions_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_institutions_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_institutions_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_institutions_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)

    def test_unrated_submissionsets_are_hidden_in_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)
        institutions = json.loads(resp.content)['objects']
        for institution in institutions:
            for submission_set in institution['submission_sets']:
                self.assertFalse(
                    submission_set['rating'] in ['None', None, ''])
