"""
Tests for the STARS credits API.

These test cases fail if run via 'manage.py test' because the test
database has no data in it, and no fixtures are defined here.  They'll
run from the REPL as doctests, if you do this:

    import stars.apps.credits.api.test as t
    import doctest
    doctest.testmod(t)
"""
import random

from stars.apps.credits.models import CreditSet
from stars.apps.credits.api.resources import CreditSetResource
from stars.apps.api.test import StarsApiTestCase, get_random_visible_resource, \
     get_random_queryset_obj, EmptyQuerysetError
from stars.apps.api.test import new_test_result, setup_test_environment

BASE_API_PATH = '/api/v1/credits/'

def get_visible_creditset():
    """Get a CreditSet exposed by the API."""
    visible_creditset = get_random_visible_resource(CreditSetResource)
    return CreditSet.objects.get(pk=visible_creditset.id)

def get_visible_category():
    """Get a Category related to a CreditSet that's exposed by the API."""
    visible_category = None
    while visible_category is None:
        visible_creditset = get_visible_creditset()
        try:
            visible_category = get_random_queryset_obj(
                visible_creditset.category_set)
        except EmptyQuerysetError:
            continue
    return visible_category

def get_visible_subcategory():
    """Get a SubCategory related to a Category exposed by the API."""
    subcategory = None
    while subcategory is None:
        try:
            category = get_visible_category()
            subcategory = get_random_queryset_obj(category.subcategory_set)
        except EmptyQuerysetError:
            continue
    return subcategory

def get_visible_credit():
    """Get a Credit related to a Subcategory that's exposed by the API."""
    credit = None
    while credit is None:
        try:
            subcategory = get_visible_subcategory()
            credit = get_random_queryset_obj(subcategory.credit_set)
        except EmptyQuerysetError:
            continue
    return credit

def get_visible_documentation_field():
    """Get a DocumentationField related to a Credit that's exposed via
    the API."""
    documentation_field = None
    while documentation_field is None:
        try:
            credit = get_visible_credit()
            documentation_field = get_random_queryset_obj(
                credit.documentationfield_set)
        except EmptyQuerysetError:
            continue
    return credit


class CreditSetResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'creditset/'

    def detail_path(self):
        creditset = get_visible_creditset()
        path = CreditSetResourceTestCase.list_path + str(creditset.id) + '/'
        return path

    def test_get_creditset_list_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditSetResourceTestCase(\
                'test_get_creditset_list_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.list_path)

    def test_get_creditset_list(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditSetResourceTestCase('test_get_creditset_list')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_creditset_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditSetResourceTestCase(\
                'test_get_creditset_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.detail_path())

    def test_get_creditset_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditSetResourceTestCase('test_get_creditset_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        path = self.detail_path()
        resp = self.get(path)
        self.assertValidJSONResponse(resp)


class CategoryResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'category/'

    def detail_path(self):
        category = get_visible_category()
        return self.list_path + str(category.id) + '/'

    def test_get_category_list_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = CategoryResourceTestCase(\
                    'test_get_category_list_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.list_path)

    def test_get_category_list(self):
        """
        >>> test_result = new_test_result()
        >>> test = CategoryResourceTestCase('test_get_category_list')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_category_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = CategoryResourceTestCase(\
                    'test_get_category_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.detail_path())

    def test_get_category_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = CategoryResourceTestCase('test_get_category_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.detail_path())
        self.assertValidJSONResponse(resp)


class SubcategoryResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'subcategory/'

    @property
    def detail_path(self):
        subcategory = get_visible_subcategory()
        return self.list_path + str(subcategory.id) + '/'

    def test_get_subcategory_list_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubcategoryResourceTestCase(\
                    'test_get_subcategory_list_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.list_path)

    def test_get_subcategory_list(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubcategoryResourceTestCase(\
                    'test_get_subcategory_list')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_subcategory_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubcategoryResourceTestCase(\
                    'test_get_subcategory_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.detail_path)

    def test_get_subcategory_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = SubcategoryResourceTestCase(\
                    'test_get_subcategory_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)


class CreditResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'credit/'

    def detail_path(self):
        credit = get_visible_credit()
        return self.list_path + str(credit.id) + '/'

    def test_get_credit_list_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditResourceTestCase('test_get_credit_list_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.list_path)

    def test_get_credit_list(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditResourceTestCase('test_get_credit_list')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_credit_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditResourceTestCase(\
                    'test_get_credit_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.detail_path())

    def test_get_credit_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = CreditResourceTestCase('test_get_credit_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.detail_path())
        self.assertValidJSONResponse(resp)


class DocumentationFieldResourceTestCase(StarsApiTestCase):

    list_path = BASE_API_PATH + 'field/'

    def detail_path(self):
        documentation_field = get_visible_documentation_field()
        return self.list_path + str(documentation_field.id) + '/'

    def test_get_documentation_field_list_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = DocumentationFieldResourceTestCase(\
                'test_get_documentation_field_list_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.list_path)

    def test_get_documentation_field_list(self):
        """
        >>> test_result = new_test_result()
        >>> test = DocumentationFieldResourceTestCase(\
                'test_get_documentation_field_list')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_documentation_field_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = DocumentationFieldResourceTestCase(\
                'test_get_documentation_field_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.detail_path())

    def test_get_documentation_field_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = DocumentationFieldResourceTestCase(\
                    'test_get_documentation_field_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        resp = self.get(self.detail_path())
        self.assertValidJSONResponse(resp)
