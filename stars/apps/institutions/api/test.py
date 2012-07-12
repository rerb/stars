"""
Tests for institutions API.
"""
import json

from stars.apps.api.test import StarsApiTestCase


class InstitutionResourceTestCase(StarsApiTestCase):

    multi_db = True
    list_path = '/api/0.1/institutions/'
    detail_path = list_path + '74/'

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
