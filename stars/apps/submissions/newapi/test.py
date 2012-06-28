"""
Tests for submissions API.
"""
from stars.apps.api.test import StarsApiTestCase

def submissions_detail_path(submissionset_id):
    path = '/api/v1/submissions/{0}/'.format(submissionset_id)
    return path


class SubmissionSetResourceTestCase(StarsApiTestCase):

    list_path = '/api/v1/submissions/'
    detail_path = list_path + '75/'

    def test_get_submissions_list_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = SubmissionSetResourceTestCase(\
                    'test_get_submissions_list_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.list_path)

    def test_get_submissions_list(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = SubmissionSetResourceTestCase(\
                    'test_get_submissions_list')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_submissions_detail_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = SubmissionSetResourceTestCase(\
                    'test_get_submissions_detail_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.detail_path)

    def test_get_submissions_detail(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = SubmissionSetResourceTestCase(\
                    'test_get_submissions_detail')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)


class CategorySubmissionResourceTestCase(StarsApiTestCase):

    list_path = submissions_detail_path(75) + 'category/'
    detail_path = list_path + '4/'

    def test_get_categorysubmission_list_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_list_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.list_path)

    def test_get_categorysubmission_list(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_list')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_categorysubmission_detail_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_detail_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.detail_path)

    def test_get_categorysubmission_detail(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = CategorySubmissionResourceTestCase(\
                    'test_get_categorysubmission_detail')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)


class SubcategorySubmissionResourceTestCase(StarsApiTestCase):

    list_path = submissions_detail_path(75) + 'subcategory/'
    detail_path = list_path + '3/'

    def test_get_subcategorysubmission_list_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_list_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.list_path)

    def test_get_subcategorysubmission_list(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_list')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_subcategorysubmission_detail_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_detail_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.detail_path)

    def test_get_subcategorysubmission_detail(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = SubcategorySubmissionResourceTestCase(\
                    'test_get_subcategorysubmission_detail')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)


class CreditSubmissionResourceTestCase(StarsApiTestCase):
    #1602
    list_path = submissions_detail_path(75) + 'credit/'
    detail_path = list_path + '17/'

    def test_get_creditsubmission_list_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_list_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.list_path)

    def test_get_creditsubmission_list(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_list')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_creditsubmission_detail_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_detail_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.detail_path)

    def test_get_creditsubmission_detail(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = CreditSubmissionResourceTestCase(\
                    'test_get_creditsubmission_detail')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)


class DocumentationFieldSubmissionResourceTestCase(StarsApiTestCase):

    detail_path = submissions_detail_path(75) + 'field/167/'

    def test_get_documentationfieldsubmission_detail_requires_auth(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = DocumentationFieldSubmissionResourceTestCase(\
                'test_get_documentationfieldsubmission_detail_requires_auth')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        self.requires_auth(self.detail_path)

    def test_get_documentationfieldsubmission_detail(self):
        """
        >>> from unittest import TestResult
        >>> from django.test.utils import setup_test_environment
        >>> result = TestResult()
        >>> test = DocumentationFieldSubmissionResourceTestCase(\
                    'test_get_documentationfieldsubmission_detail')
        >>> test.run(result)
        >>> result.testsRun
        1
        >>> result.errors + result.failures
        []
        >>>
        """
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)
