"""
Tests for the STARS credits API.
"""
from stars.apps.api.test import StarsApiTestCase

BASE_API_PATH = '/api/0.1/credits/'


class CreditSetResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'creditset/'
    detail_path = list_path + '2/'

    def test_get_creditset_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_creditset_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_creditset_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_creditset_detail(self):
        path = self.detail_path
        resp = self.get(path)
        self.assertValidJSONResponseNotError(resp)


class CategoryResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'category/'
    detail_path = list_path + '12/'

    def test_get_category_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_category_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_category_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_category_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponseNotError(resp)


class SubcategoryResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'subcategory/'
    detail_path = list_path + '10/'

    def test_get_subcategory_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_subcategory_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_subcategory_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_subcategory_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponseNotError(resp)


class CreditResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'credit/'
    detail_path = list_path + '241/'

    def test_get_credit_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_credit_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_credit_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_credit_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponseNotError(resp)


class DocumentationFieldResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'field/'
    detail_path = list_path + '473/'

    def test_get_documentation_field_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_documentation_field_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_documentation_field_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_documentation_field_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponseNotError(resp)
