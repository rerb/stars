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

    @property
    def next_button(self):
        """Returns the Next button."""
        buttons = self.selenium.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == 'Next':
                return button
        raise Exception('no Next button?')

    @property
    def final_purchase_subscription_button(self):
        """Returns the final Purchase Subscription button."""
        buttons = self.selenium.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == 'Purchase Subscription':
                return button
        raise Exception('no Purchase Subscription button?')

    def test_purchase_subscription_later(self):
        """Is a new Subscription created when I pay later?"""
        # Remember how many Subscriptions there are before purchase:
        num_submission_sets_before_purchase = Subscription.objects.count()

        # Purchase a subscription:
        purchase_subscription_button = self.selenium.find_element_by_link_text(
            'Purchase STARS Participant Subscription')
        purchase_subscription_button.click()

        # Subscription Price View -- just click through it.
        self.next_button.click()

        # Pay later:
        pay_later_checkbox = self.selenium.find_element_by_xpath(
            "(//input[@name='pay_when'])[2]")
        pay_later_checkbox.click()
        self.next_button.click()

        # Purchase it!
        self.final_purchase_subscription_button.click()

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
        self.next_button.click()

        # Pay now:
        pay_now_checkbox = self.selenium.find_element_by_xpath(
            "(//input[@name='pay_when'])[1]")
        pay_now_checkbox.click()
        self.next_button.click()

        # Credit card info:
        text_inputs = {'id_card_number': '4007000000027',
                       'id_exp_month': str(date.today().month),
                       'id_exp_year': str(date.today().year + 1)}

        for id, text in text_inputs.items():
            input = self.selenium.find_element_by_id(id)
            input.clear()
            input.send_keys(text)

        self.final_purchase_subscription_button.click()

        # Was a Subscription created?
        self.assertEqual(Subscription.objects.count(),
                         num_submission_sets_before_purchase + 1)
