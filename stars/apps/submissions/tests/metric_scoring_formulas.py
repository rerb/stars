"""
    Test the values passed to the point calculation formula
"""

from .metric_base_test import BaseMetricTest

from stars.apps.submissions.models import CreditUserSubmission


class MetricScoringFormulaTest(BaseMetricTest):

    def testSequence(self):
        """ Run the other tests"""
        self.runTestEnv()
        self.runSwapAndPrint()

    def evaluateFieldKey(self, key):
        self.assertEqual(key['A'], 4.0)
        self.assertEqual(key['B'], 2.0)

    def runSwapAndPrint(self):

        # submit the credit with some simple initial values
        post_dict = {
            "responsible_party": self.rp.id,
            "responsible_party_confirm": True,
            "submission_status": 'c',
            "NumericSubmission_1-value": "4",
            "NumericSubmission_1-metric_value": "",
            "NumericSubmission_2-value": "2",
            "NumericSubmission_2-metric_value": ""
        }
        response = self.client.post(self.cus.get_submit_url(), post_dict)
        self.assertEqual(response.status_code, 302)

        self.cus = CreditUserSubmission.objects.all()[0]
        self.evaluateFieldKey(self.cus.get_submission_field_key())

        self.institution.prefers_metric_system = True
        self.institution.save()

        self.cus = CreditUserSubmission.objects.all()[0]
        self.evaluateFieldKey(self.cus.get_submission_field_key())

        post_dict = {
            "responsible_party": self.rp.id,
            "responsible_party_confirm": True,
            "submission_status": 'c',
            "NumericSubmission_1-value": "",
            "NumericSubmission_1-metric_value": "2",
            "NumericSubmission_2-value": "",
            "NumericSubmission_2-metric_value": "4"
        }
        response = self.client.post(self.cus.get_submit_url(), post_dict)

        self.cus = CreditUserSubmission.objects.all()[0]
        self.evaluateFieldKey(self.cus.get_submission_field_key())
