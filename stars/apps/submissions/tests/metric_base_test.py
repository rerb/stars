"""
    Base test class for multiple metric tests
"""

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

from stars.test_factories import (
    CreditFactory,
    DocumentationFieldFactory,
    InstitutionFactory,
    ResponsiblePartyFactory)
from stars.apps.credits.models import Unit
from stars.apps.submissions.models import (
    NumericSubmission,
    CreditUserSubmission)
from stars.apps.registration.utils import init_starsaccount, init_submissionset


class BaseMetricTest(TestCase):

    fixtures = ["notification_emailtemplate_tests.json"]

    def setUp(self):
        self.us_unit = Unit(name='imperial units',
                            is_metric=False,
                            ratio=.5)  # 1 us is .5 metric
        self.us_unit.save()
        # metric value is twice the us unit
        self.metric_unit = Unit(name="metric units",
                                is_metric=True,
                                ratio=2,  # 1 metric is 2 us
                                equivalent=self.us_unit)
        self.metric_unit.save()
        self.us_unit.equivalent = self.metric_unit
        self.us_unit.save()

        self.credit = CreditFactory(
            identifier="c1",
            title='c1',
            point_value="20"  # give us room to work with
        )
        self.credit_set = self.credit.get_creditset()
        self.credit_set.version = "2.0"
        self.credit_set.save()

        # Note, df1 must be between 1 and 10
        self.df1 = DocumentationFieldFactory(
            title="A",
            credit=self.credit,
            units=self.us_unit,
            type='numeric',
            min_range="1",
            max_range="10",
            ordinal="0"
        )
        self.df2 = DocumentationFieldFactory(
            title="B",
            credit=self.credit,
            units=self.us_unit,
            type='numeric',
            ordinal="1"
        )

        # Validation and point formulas for the credit
        self.credit.formula = "points = A + B"
        self.credit.validation_rules = """
if B >= A:
    errors['A'] = "A must be bigger than B!"
        """
        self.credit.save()

        self.user = User(username="test")
        self.user.set_password("test")
        self.user.save()

        self.buildSubmissionEnvironmentForCreditSet(
            credit_set=self.credit_set,
            user=self.user
        )
        self.cus = CreditUserSubmission.objects.all()[0]
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)

        self.client = Client()
        self.client.login(username='test', password='test')

    def runTestEnv(self):
        self.assertEqual(self.df1.identifier, "A")
        self.assertEqual(self.df2.identifier, "B")
        self.assertFalse(self.institution.prefers_metric_system)
        self.assertEqual(NumericSubmission.objects.all().count(), 2)

        response = self.client.get(self.cus.get_submit_url())
        self.assertEqual(response.status_code, 200)

    def buildSubmissionEnvironmentForCreditSet(
        self,
        credit_set,
        user,
        user_level='admin'
    ):
        """
            Provides a quick way to run end-to-end tests on a creditset

            Once this has been run, you should be able to run the test client
            with:
                >>> c.get("/tool/institution/submission/1/")
            and test credit individually

            creates: SubmissionSet, Institution, and StarsAccount and more
        """
        self.institution = InstitutionFactory()
        self.account = init_starsaccount(user, self.institution)
        self.submission_set = init_submissionset(self.institution, user)

        # Create CreditUser Submissions and DocumentationFieldSubmissions
        self.submission_set.init_credit_submissions()
        for cus in CreditUserSubmission.objects.all():
            cus.get_submission_fields()
        self.rp = ResponsiblePartyFactory(institution=self.institution)
