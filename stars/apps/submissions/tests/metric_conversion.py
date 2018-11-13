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

        - test data corrections
            submit a data correction using metric
            submit a data correction using imperial
"""

from .metric_base_test import BaseMetricTest

from stars.apps.submissions.models import (
    NumericSubmission,
    CreditUserSubmission,
    DataCorrectionRequest,
    ReportingFieldDataCorrection)


class MetricConversionTest(BaseMetricTest):

    def testConversion(self):
        self.runTestEnv()
        self.runTestImperial()
        self.runTestMetric()
        self.runTestPreferenceSwitch()
        self.runTestNullValues()

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
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)

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
        self.institution.prefers_metric_system = True
        self.institution.save()

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
        self.institution.prefers_metric_system = False
        self.institution.save()

        # values don't change
        self.ns1 = NumericSubmission.objects.get(documentation_field=self.df1)
        self.ns2 = NumericSubmission.objects.get(documentation_field=self.df2)
        self.assertEqual(self.ns1.value, 8.2)
        self.assertEqual(self.ns2.value, 6.6)
        self.assertEqual(self.ns1.metric_value, 4.1)
        self.assertEqual(self.ns2.metric_value, 3.3)

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
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)

        self.institution.prefers_metric_system = True
        self.institution.save()

        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)
