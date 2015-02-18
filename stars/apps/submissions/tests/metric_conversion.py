"""
    Tests for apps.submissions.models.NumericSubmission metric functionality

    The existing NumericSubmission test doesn't catch a particular bug
"""

"""
    Test logic...

    Init:
        Create an invented 2:1 metric unit
        Generate a CreditSet with one Credit
            with two NumericSubmissionFields with the invented unit
            add min/max validation rules for one
            add formula validation that one is greater than the other
        Create a Institution who doesn't use metric
        Create a user for the Institution with admin access
        Create a SubmissionSet for that Institution

    Actions:
        - Test imperial
        Set the fields to valid numbers and submit the credit as complete
            confirm submission accuracy and values are consistent
            confirm that the metric_values are calculated
        Test with min/max verification failing
            confirm submission doesn't go through
            confirm values don't change
        Submit with formula verification failing
            confirm failure
            confirm values don't change
        Fix verification and save as "in progress"
            confirm metric values are accurate

        - Test metric
        Set the institution preference to metric
            confirm that the values for the credit are displayed appropriately
        Save credit as in progress
            values don't change
        Save credit as complete
            values don't change
        Change the values slightly and save as in progress
            confirm that the values and metric_values are accurate
        Test verification (as above)
        Fix verification and save as "complete"
            confirm metric values are accurate
        Tweak values and save as "in progress"
                confirm metric values are accurate

        Set institution pref back to imperial
            confirm values don't change and are displayed appropriately
        Save credit as in progress
            values don't change
        Save credit as complete
            values don't change

        Try submitting null values to fields
"""

from unittest import TestCase

from stars.test_factories import (
    CreditFactory,
    DocumentationFieldFactory,
    InstitutionFactory,
    SubmissionSetFactory,
    NumericDocumentationFieldSubmissionFactory,
    CreditUserSubmissionFactory,
    DocumentationFieldFactory,
    ResponsiblePartyFactory)
from stars.apps.credits.models import Unit
from stars.apps.submissions.models import (
    NumericSubmission,
    CreditUserSubmission)
from stars.apps.registration.utils import init_starsaccount, init_submissionset

from django.test import Client
from django.contrib.auth.models import User


class MetricConversionTest(TestCase):

    def setUp(self):
        self.us_unit = Unit(is_metric=False,
                            ratio=.5) # 1 us is .5 metric
        self.us_unit.save()
        # metric value is twice the us unit
        self.metric_unit = Unit(is_metric=True,
                                ratio=2, # 1 metric is 2 us
                                equivalent=self.us_unit)
        self.metric_unit.save()
        self.us_unit.equivalent = self.metric_unit
        self.us_unit.save()

        self.credit = CreditFactory(
            identifier="c1",
            title='c1',
            point_value="20" # give us room to work with
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

    def testConversion(self):
        self.client = Client()
        self.client.login(username='test', password='test')
        self.runTestEnv()
        self.runTestImperial()
        self.runTestMetric()
        self.runTestPreferenceSwitch()
        self.runTestNullValues()

    def runTestEnv(self):
        self.assertEqual(self.df1.identifier, "A")
        self.assertEqual(self.df2.identifier, "B")
        self.assertFalse(self.institution.prefers_metric_system)
        self.assertEqual(NumericSubmission.objects.all().count(), 2)

        response = self.client.get(self.cus.get_submit_url())
        self.assertEqual(response.status_code, 200)

    def runTestImperial(self):
        """
            Set the fields to valid numbers and submit the credit as complete
                confirm submission accuracy and values are consistent
                confirm that the metric_values are calculated
            Test with min/max verification failing
                confirm submission doesn't go through
                confirm values don't change
            Submit with formula verification failing
                confirm failure
                confirm values don't change
            Fix verification and save as "in progress"
                confirm metric values are accurate
        """
        print "testing imperial"

        # just submit and save
        post_dict = {
            "responsible_party": self.rp.id,
            "responsible_party_confirm": True,
            "submission_status": 'p',
            "NumericSubmission_1-value": 2,
            "NumericSubmission_1-metric_value": "",
            "NumericSubmission_2-value": 1,
            "NumericSubmission_2-metric_value": ""
        }
        print "Testing saving as 'In Progress'"
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)

        print """
            Set the fields to valid numbers and submit the credit as complete
                confirm submission accuracy and values are consistent
                confirm that the metric_values are calculated"""
        post_dict['submission_status'] = 'c'
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)

        self.cus = CreditUserSubmission.objects.all()[0]
        self.assertEqual(self.cus.submission_status, 'c')

        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)

        # confirm submission accuracy and values are consistent
        self.assertEqual(self.ns1.value, 2)
        self.assertEqual(self.ns2.value, 1)

        # confirm that the metric_values are calculated
        self.assertEqual(self.ns1.metric_value, 1)
        self.assertEqual(self.ns2.metric_value, .5)

        print """
            Test with min/max verification failing
                confirm submission doesn't go through
                confirm values don't change"""

        # above range
        post_dict['NumericSubmission_1-value'] = 11
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 200)
        # below range
        post_dict['NumericSubmission_1-value'] = 0
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 200)
        # values don't change
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.assertEqual(self.ns1.value, 2)
        self.assertEqual(self.ns1.metric_value, 1)

        print """
            Submit with formula verification failing
                confirm failure
                confirm values don't change"""
        # set B as greater than A
        post_dict['NumericSubmission_1-value'] = 5
        post_dict['NumericSubmission_2-value'] = 6
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 200)
        # values don't change
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.assertEqual(self.ns1.value, 2)
        self.assertEqual(self.ns2.value, 1)
        self.assertEqual(self.ns1.metric_value, 1)
        self.assertEqual(self.ns2.metric_value, .5)

        print """
            Fix verification and save as 'in progress'
                confirm metric values are accurate
        """
        post_dict['NumericSubmission_1-value'] = 6
        post_dict['NumericSubmission_2-value'] = 5
        post_dict['submission_status'] = 'p'
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)
        self.assertEqual(self.ns1.value, 6)
        self.assertEqual(self.ns2.value, 5)
        self.assertEqual(self.ns1.metric_value, 3)
        self.assertEqual(self.ns2.metric_value, 2.5)

    def runTestMetric(self):
        """
        Set the institution preference to metric
            confirm that the values for the credit are displayed appropriately
        Save credit as in progress
            values don't change
        Save credit as complete
            values don't change
        Change the values slightly and save as in progress
            confirm that the values and metric_values are accurate
        Test verification (as above)
        Fix verification and save as "in progress"
            confirm metric values are accurate
        """

        print "Testing Metric"
        self.institution.prefers_metric_system = True
        self.institution.save()

        print """
            Save credit as in progress
                values shouldn't change
        """
        post_dict = {
            "responsible_party": self.rp.id,
            "responsible_party_confirm": True,
            "submission_status": 'c',
            "NumericSubmission_1-value": "",
            "NumericSubmission_1-metric_value": "3",
            "NumericSubmission_2-value": "",
            "NumericSubmission_2-metric_value": "2.5"
        }
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)
        self.assertEqual(self.ns1.value, 6)
        self.assertEqual(self.ns2.value, 5)
        self.assertEqual(self.ns1.metric_value, 3)
        self.assertEqual(self.ns2.metric_value, 2.5)

        print """
            Test with min/max verification failing
                confirm submission doesn't go through
                confirm values don't change"""

        # above range
        post_dict['NumericSubmission_1-metric_value'] = 5.5
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 200)
        # below range
        post_dict['NumericSubmission_1-value'] = 0
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 200)
        # values don't change
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.assertEqual(self.ns1.value, 6)
        self.assertEqual(self.ns1.metric_value, 3)

        print """
            Submit with formula verification failing
                confirm failure
                confirm values don't change"""
        # set B as greater than A
        post_dict['NumericSubmission_1-metric_value'] = 3
        post_dict['NumericSubmission_2-metric_value'] = 4
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 200)
        # values don't change
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)
        self.assertEqual(self.ns1.value, 6)
        self.assertEqual(self.ns2.value, 5)
        self.assertEqual(self.ns1.metric_value, 3)
        self.assertEqual(self.ns2.metric_value, 2.5)

        print """
            Fix verification and save as "complete"
                confirm metric values are accurate"""
        # set A as greater than B
        post_dict['submission_status'] = "c"
        post_dict['NumericSubmission_1-metric_value'] = 4
        post_dict['NumericSubmission_2-metric_value'] = 3.2
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)
        # values don't change
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)
        self.assertEqual(self.ns1.value, 8)
        self.assertEqual(self.ns2.value, 6.4)
        self.assertEqual(self.ns1.metric_value, 4)
        self.assertEqual(self.ns2.metric_value, 3.2)

        print """
            Tweak values and save as "in progress"
                confirm metric values are accurate"""

        post_dict['submission_status'] = "p"
        post_dict['NumericSubmission_1-metric_value'] = 4.1
        post_dict['NumericSubmission_2-metric_value'] = 3.3
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)
        # values don't change
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)
        self.assertEqual(self.ns1.value, 8.2)
        self.assertEqual(self.ns2.value, 6.6)
        self.assertEqual(self.ns1.metric_value, 4.1)
        self.assertEqual(self.ns2.metric_value, 3.3)

    def runTestPreferenceSwitch(self):
        """
        Set institution pref back to imperial
            confirm values don't change and are displayed appropriately
        Save credit as in progress
            with new values
        Save credit as complete
            confirm new values
        """

        print "Reverting back to imperial"
        self.institution.prefers_metric_system = False
        self.institution.save()

        print """
            Set institution pref back to imperial
                confirm values don't change and are displayed appropriately"""
        # values don't change
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)
        self.assertEqual(self.ns1.value, 8.2)
        self.assertEqual(self.ns2.value, 6.6)
        self.assertEqual(self.ns1.metric_value, 4.1)
        self.assertEqual(self.ns2.metric_value, 3.3)

        print """
            Save credit as in progress
                confirm new values
        """
        post_dict = {
            "responsible_party": self.rp.id,
            "responsible_party_confirm": True,
            "submission_status": 'p',
            "NumericSubmission_1-value": "7.5",
            "NumericSubmission_1-metric_value": "",
            "NumericSubmission_2-value": "6.5",
            "NumericSubmission_2-metric_value": ""
        }
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)

        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)
        self.assertEqual(self.ns1.value, 7.5)
        self.assertEqual(self.ns2.value, 6.5)
        self.assertEqual(self.ns1.metric_value, 3.75)
        self.assertEqual(self.ns2.metric_value, 3.25)

        print """
            Save credit as complete
                confirm new values
        """
        post_dict['submission_status'] = 'c'
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)

        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)
        self.assertEqual(self.ns1.value, 7.5)
        self.assertEqual(self.ns2.value, 6.5)
        self.assertEqual(self.ns1.metric_value, 3.75)
        self.assertEqual(self.ns2.metric_value, 3.25)

    def runTestNullValues(self):
        """
            Test null value submissions
        """

        print "testing null values"

        # just submit and save
        post_dict = {
            "responsible_party": self.rp.id,
            "responsible_party_confirm": True,
            "submission_status": 'p',
            "NumericSubmission_1-value": "",
            "NumericSubmission_1-metric_value": "",
            "NumericSubmission_2-value": "",
            "NumericSubmission_2-metric_value": ""
        }
        print "Testing saving as 'In Progress'"
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)

        print "switching to metric"
        self.institution.prefers_metric_system = True
        self.institution.save()

        print "Testing saving as 'In Progress'"
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)


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
