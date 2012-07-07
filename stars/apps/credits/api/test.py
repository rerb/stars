"""
Tests for the STARS credits API.
"""
from stars.apps.api.test import StarsApiTestCase, get_random_queryset_obj
from stars.apps.credits.models import CreditSet, Category, Subcategory, \
     Credit, DocumentationField

BASE_API_PATH = '/api/0.1/credits/'


class CreditSetResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'creditset/'

    def detail_path(self):
        random_creditset = get_random_queryset_obj(CreditSet.objects.all())
        return self.list_path + str(random_creditset.id) + '/'

    def test_get_creditset_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_creditset_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_creditset_detail_requires_auth(self):
        self.requires_auth(self.detail_path())

    def test_get_creditset_detail(self):
        path = self.detail_path()
        resp = self.get(path)
        self.assertValidJSONResponseNotError(resp)


class CategoryResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'category/'

    def detail_path(self):
        random_category = get_random_queryset_obj(Category.objects.all())
        return self.list_path + str(random_category.id) + '/'

    def test_get_category_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_category_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_category_detail_requires_auth(self):
        self.requires_auth(self.detail_path())

    def test_get_category_detail(self):
        resp = self.get(self.detail_path())
        self.assertValidJSONResponseNotError(resp)


class SubcategoryResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'subcategory/'

    def detail_path(self):
        random_subcategory = get_random_queryset_obj(Subcategory.objects.all())
        return self.list_path + str(random_subcategory.id) + '/'

    def test_get_subcategory_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_subcategory_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_subcategory_detail_requires_auth(self):
        self.requires_auth(self.detail_path())

    def test_get_subcategory_detail(self):
        resp = self.get(self.detail_path())
        self.assertValidJSONResponseNotError(resp)


class CreditResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'credit/'

    def detail_path(self):
        random_credit = get_random_queryset_obj(Credit.objects.all())
        return self.list_path + str(random_credit.id) + '/'

    def test_get_credit_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_credit_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_credit_detail_requires_auth(self):
        self.requires_auth(self.detail_path())

    def test_get_credit_detail(self):
        resp = self.get(self.detail_path())
        self.assertValidJSONResponseNotError(resp)


class DocumentationFieldResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'field/'

    def detail_path(self):
        random_field = get_random_queryset_obj(DocumentationField.objects.all())
        return self.list_path + str(random_field.id) + '/'

    def test_get_documentation_field_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_documentation_field_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_documentation_field_detail_requires_auth(self):
        self.requires_auth(self.detail_path())

    def test_get_documentation_field_detail(self):
        resp = self.get(self.detail_path())
        self.assertValidJSONResponseNotError(resp)
