"""
    Functional tests for the subscription renewal process.
"""
from datetime import date

from django.core import mail
from selenium.webdriver.common.by import By

from stars.apps.institutions.models import Subscription
from stars.apps.tests.live_server import StarsLiveServerTest


class RenewalTest(StarsLiveServerTest):

    fixtures = ['notification_emailtemplate_tests.json']

    def setUp(self):
        super(RenewalTest, self).setUp()
        self.go_to_reporting_tool()

    def test_purchase_subscription_later(self):
        """Is a new Subscription created when I pay later?"""
        # Remember how many Subscriptions there are before purchase:
        num_submission_sets_before_purchase = Subscription.objects.count()

        # Purchase a subscription:
        purchase_subscription_button = self.selenium.find_element_by_link_text(
            'Purchase STARS Participant Subscription')
        purchase_subscription_button.click()

        # Subscription Price View -- just click through it.
        submit_button = self.patiently_find(look_for='submit_button',
                                            by=By.ID)
        submit_button.click()

        # Pay later:
        pay_later_checkbox = self.selenium.find_element_by_xpath(
            "(//input[@name='pay_when'])[2]")
        pay_later_checkbox.click()

        continue_submit_button = self.selenium.find_element_by_id(
            'submit_button')
        continue_submit_button.click()

        # Purchase it!
        purchase_submit_button = self.selenium.find_element_by_id(
            'submit_button')
        purchase_submit_button.click()

        # Was a Subscription created?
        self.assertEqual(Subscription.objects.count(),
                         num_submission_sets_before_purchase + 1)

    def test_purchase_subscription_now(self):
        """Is a new Subscription created when I pay now?"""
        # Remember how many Subscriptions there are before purchase:
        num_submission_sets_before_purchase = Subscription.objects.count()

        # Purchase a subscription:
        purchase_subscription_button = self.selenium.find_element_by_link_text(
            'Purchase STARS Participant Subscription')
        purchase_subscription_button.click()

        # Subscription Price View -- just click through it.
        submit_button = self.patiently_find(look_for='submit_button',
                                            by=By.ID)
        submit_button.click()

        # Pay now:
        pay_now_checkbox = self.selenium.find_element_by_xpath(
            "(//input[@name='pay_when'])[1]")
        pay_now_checkbox.click()

        purchase_submit_button = self.selenium.find_element_by_id(
            'submit_button')
        purchase_submit_button.click()

        # Credit card info:
        text_inputs = {'id_card_number': '4007000000027',
                       'id_exp_month': str(date.today().month),
                       'id_exp_year': str(date.today().year + 1)}

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
