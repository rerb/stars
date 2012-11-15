"""
    Functional tests for the subscription renewal process.
"""
from datetime import date

from django.core import mail

from stars.apps.institutions.models import Subscription
from stars.apps.tests.live_server import StarsLiveServerTest


class RenewalTest(StarsLiveServerTest):

    fixtures = ['notification_emailtemplate_tests.json']

    def setUp(self):
        super(RenewalTest, self).setUp()
        self.go_to_reporting_tool()

    def tearDown(self):
        super(RenewalTest, self).tearDown()
        mail_messages_that_are_not_errors = [ msg for msg in mail.outbox if
                                              'ERROR:' not in msg.subject ]
        self.assertEqual(len(mail_messages_that_are_not_errors), 1)

    def go_to_reporting_tool(self):
        reporting_tool_tab = self.selenium.find_element_by_link_text(
            'Reporting')
        reporting_tool_tab.click()

    def test_purchase_subscription_later(self):
        """Is a new Subscription created when I pay later?
        (And is an email sent, too?)"""
        # Remember how many Subscriptions there are before purchase:
        num_submission_sets_before_purchase = Subscription.objects.count()

        # Purchase a subscription:
        purchase_subscription_button = self.selenium.find_element_by_link_text(
            'Purchase STARS Participant Subscription')
        purchase_subscription_button.click()

        # Pay later:
        pay_later_checkbox = self.selenium.find_element_by_xpath(
            "(//input[@name='pay_when'])[2]")
        pay_later_checkbox.click()

        purchase_submit_button = self.selenium.find_element_by_id(
            'submit_button')
        purchase_submit_button.click()

        # Promo code page:
        promo_code_submit_button = self.selenium.find_element_by_id(
            'submit_button')
        promo_code_submit_button.click()

        # Was a Subscription created?
        self.assertEqual(Subscription.objects.count(),
                         num_submission_sets_before_purchase + 1)

    def test_purchase_subscription_now(self):
        """Is a new Subscription created when I pay now?
        (And is an email sent, too?)"""
        # Remember how many Subscriptions there are before purchase:
        num_submission_sets_before_purchase = Subscription.objects.count()

        # Purchase a subscription:
        purchase_subscription_button = self.selenium.find_element_by_link_text(
            'Purchase STARS Participant Subscription')
        purchase_subscription_button.click()

        # Pay now:
        pay_now_checkbox = self.selenium.find_element_by_name('pay_when')
        pay_now_checkbox.click()

        purchase_submit_button = self.selenium.find_element_by_id(
            'submit_button')
        purchase_submit_button.click()

        # Credit card info:
        text_inputs = {'id_name_on_card': 'asdf',
                       'id_card_number': '4007000000027',
                       'id_exp_month': str(date.today().month),
                       'id_exp_year': str(date.today().year + 1),
                       'id_cv_code': '123',
                       'id_billing_address': 'asdf',
                       'id_billing_city': 'asdf',
                       'id_billing_state': 'pa',
                       'id_billing_zipcode': '12345'}

        for id, text in text_inputs.items():
            input = self.selenium.find_element_by_id(id)
            input.clear()
            input.send_keys(text)

        credit_card_submit_button = self.selenium.find_element_by_id(
            'submit_button')
        credit_card_submit_button.click()

        # Was a Subscription created?
        self.assertEqual(Subscription.objects.count(),
                         num_submission_sets_before_purchase + 1)
