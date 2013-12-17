"""
    Functional tests for the subscription renewal process.
"""
from stars.apps.institutions.models import Subscription
from stars.apps.institutions.tests.subscription import GOOD_CREDIT_CARD
from stars.apps.tests.live_server import StarsLiveServerTest

LATER = 'later'
NOW = 'now'


class CannotFindElementError(Exception):
    pass


class RenewalTest(StarsLiveServerTest):

    fixtures = ['notification_emailtemplate_tests.json']

    def setUp(self):
        super(RenewalTest, self).setUp()
        self.go_to_reporting_tool()

    def get_button_with_text(self, text):
        buttons = self.selenium.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == text:
                return button
        raise CannotFindElementError('no {text} button?'.format(
            text=text))

    @property
    def next_button(self):
        """Returns the Next button."""
        return self.get_button_with_text('Next')
 
    @property
    def final_purchase_subscription_button(self):
        """Returns the final Purchase Subscription button."""
        buttons = self.selenium.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == 'Purchase Subscription':
                return button
        raise Exception('no Purchase Subscription button?')

    # payment option:
    def get_payment_options_radio_buttons(self):
        """Returns the payment options radio buttons."""
        input_buttons = self.selenium.find_elements_by_tag_name('input')
        radio_buttons = [ib for ib in input_buttons
                         if ib.get_attribute('type') == 'radio']
        return radio_buttons

    def get_pay_now_radio_button(self):
        """Returns the radio button that indicates 'Pay now please'."""
        for radio_button in self.get_payment_options_radio_buttons():
            if radio_button.get_attribute('value') == Subscription.PAY_NOW:
                return radio_button
        raise CannotFindElementError('no Pay Now radio button?')

    def get_pay_later_radio_button(self):
        """Returns the radio button that indicates 'Pay later please'."""
        for radio_button in self.get_payment_options_radio_buttons():
            if radio_button.get_attribute('value') == Subscription.PAY_LATER:
                return radio_button
        raise CannotFindElementError('no Pay Later radio button?')

    @property
    def payment_option(self):
        if self.get_pay_now_radio_button().is_selected():
            return NOW
        elif self.get_pay_later_radio_button().is_selected():
            return LATER
        else:
            return None

    @payment_option.setter
    def payment_option(self, value):
        self.assertIn(value, [NOW, LATER])
        if value == NOW:
            button = self.get_pay_now_radio_button()
        else:
            button = self.get_pay_later_radio_button()
        button.click()
        self.next_button.click()

    def get_input_elements(self, type):
        input_elements = self.selenium.find_elements_by_tag_name('input')
        type_elements = [ib for ib in input_elements
                         if ib.get_attribute("type") == type]
        return type_elements

    def get_text_input_element(self, end_of_id):
        """Returns (the first) text input element with an
        ID that ends with `end_of_id`.

        Useful for locating elements on pages managed by
        a FormWizard, which mangles element IDs.
        """
        text_input_elements = self.get_input_elements(type="text")
        for text_input_element in text_input_elements:
            if text_input_element.get_attribute("id").endswith(end_of_id):
                return text_input_element
        raise CannotFindElementError(
            "no {0} element?".format(end_of_id.replace("_",
                                                       " ")))

    # credit card number:
    @property
    def credit_card_number_element(self):
        credit_card_number_element = self.get_text_input_element(
            "card_number")
        return credit_card_number_element

    @property
    def credit_card_number(self):
        return self.credit_card_number_element.text

    @credit_card_number.setter
    def credit_card_number(self, value):
        self.credit_card_number_element.clear()
        self.credit_card_number_element.send_keys(value)

    # credit card expiration month:
    @property
    def credit_card_expiration_month_element(self):
        credit_card_expiration_month_element = self.get_text_input_element(
            "exp_month")
        return credit_card_expiration_month_element

    @property
    def credit_card_expiration_month(self):
        return self.credit_card_expiration_month_element.text

    @credit_card_expiration_month.setter
    def credit_card_expiration_month(self, value):
        self.credit_card_expiration_month_element.clear()
        self.credit_card_expiration_month_element.send_keys(value)

    @property
    def credit_card_expiration_year_element(self):
        credit_card_expiration_year_element = self.get_text_input_element(
            "exp_year")
        return credit_card_expiration_year_element

    # credit card expiration year:
    @property
    def credit_card_expiration_year(self):
        return self.credit_card_expiration_year_element.text

    @credit_card_expiration_year.setter
    def credit_card_expiration_year(self, value):
        self.credit_card_expiration_year_element.clear()
        self.credit_card_expiration_year_element.send_keys(value)

    def test_purchase_subscription_pay_later(self):
        """Is a new Subscription created when I pay later?"""
        # Remember how many Subscriptions there are before purchase:
        num_submission_sets_before_purchase = Subscription.objects.count()

        # Purchase a subscription:
        purchase_subscription_button = self.selenium.find_element_by_link_text(
            'Purchase STARS Full Access Subscription')
        purchase_subscription_button.click()

        # Subscription Price View -- just click through it.
        self.next_button.click()

        # Pay later:
        self.payment_option = LATER

        # Purchase it!
        self.final_purchase_subscription_button.click()

        # Was a Subscription created?
        self.assertEqual(Subscription.objects.count(),
                         num_submission_sets_before_purchase + 1)

    def test_purchase_subscription_pay_now(self):
        """Is a new Subscription created when I pay now?"""
        # Remember how many Subscriptions there are before purchase:
        num_submission_sets_before_purchase = Subscription.objects.count()

        # Purchase a subscription:
        purchase_subscription_button = self.selenium.find_element_by_link_text(
            'Purchase STARS Full Access Subscription')
        purchase_subscription_button.click()

        # Subscription Price View -- just click through it.
        self.next_button.click()

        # Pay now:
        self.payment_option = NOW

        self.credit_card_number = GOOD_CREDIT_CARD
        self.credit_card_expiration_month = "12"
        self.credit_card_expiration_year = "2020"

        self.final_purchase_subscription_button.click()

        # Was a Subscription created?
        self.assertEqual(Subscription.objects.count(),
                         num_submission_sets_before_purchase + 1)
