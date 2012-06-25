"""
Tests for institutions API.

These test cases fail if run via 'manage.py test' because the test
database has no data in it, and no fixtures are defined here.  They'll
run from the REPL as doctests, if you do this:

    import stars.apps.institutions.api.test as t
    import doctest
    doctest.testmod(t)
"""
import stars.apps.api.test as stars_api_test
from stars.apps.api.test import StarsApiTestCase, get_random_resource, \
     get_random_queryset_obj, new_test_result, setup_test_environment, \
     EmptyQuerysetError
from stars.apps.institutions.api.resources import InstitutionResource

def institutions_detail_path(institution=None):
    institution = institution or get_random_resource(InstitutionResource)
    path = '/api/v1/institutions/{0}/'.format(institution.id)
    return path


class InstitutionResourceTestCase(stars_api_test.StarsApiTestCase):

    list_path = '/api/v1/institutions/'

    def test_get_institutions_list_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = InstitutionResourceTestCase(\
                'test_get_institutions_list_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(self.list_path)

    def test_get_institutions_list(self):
        """
        >>> test_result = new_test_result()
        >>> test = InstitutionResourceTestCase('test_get_institutions_list')
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

    def test_get_institutions_detail_requires_auth(self):
        """
        >>> test_result = new_test_result()
        >>> test = InstitutionResourceTestCase(\
                'test_get_institutions_detail_requires_auth')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        self.requires_auth(institutions_detail_path())

    def test_get_institutions_detail(self):
        """
        >>> test_result = new_test_result()
        >>> test = InstitutionResourceTestCase('test_get_institutions_detail')
        >>> test.run(test_result)
        >>> test_result.testsRun
        1
        >>> test_result.errors
        []
        >>> test_result.failures
        []
        """
        path = institutions_detail_path()
        resp = self.get(path)
        self.assertValidJSONResponse(resp)
