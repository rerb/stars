from logging import getLogger, CRITICAL
import urlparse

from django.core.urlresolvers import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from stars.apps.institutions.models import Subscription
from stars.apps.tests.live_server import StarsLiveServerTest
from stars.test_factories import (OrganizationFactory,
                                  ValueDiscountFactory)

PARTICIPANT = 'participant'
RESPONDENT = 'respondent'

LATER = 'later'
NOW = 'now'

# Don't bother me:
logger = getLogger('stars')
logger.setLevel(CRITICAL)


class CannotFindElementError(Exception):
    pass


class RegistrationWizardLiveServerTest(StarsLiveServerTest):

    def setUp(self, *args, **kwargs):
        super(RegistrationWizardLiveServerTest, self).setUp(*args, **kwargs)
        self.institution.aashe_id = None  # not registered for STARS
        self.institution.save()
        self.school = OrganizationFactory(
            org_type="Four Year Institution",
            country="United States of America")
        self.freebie_code = ValueDiscountFactory(amount=0,
                                                 percentage=100)
        self.summon_the_wizard()

    @property
    def promo_code_element(self):
        return self.patiently_find(look_for='promo_code',
                                   by=By.CLASS_NAME)

    @property
    def promo_code(self):
        return self.promo_code_element.text

    @promo_code.setter
    def promo_code(self, value):
        self.promo_code_element.clear()
        self.promo_code_element.send_keys(value)

    @property
    def apply_promo_code_button(self):
        """Returns the Apply Promo Code button."""
        apply_promo_code_button = self.patiently_find(
            look_for='apply-promo-code-button', by=By.ID)
        return apply_promo_code_button

    @property
    def next_button(self):
        """Returns the Next button."""
        buttons = self.selenium.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == 'Next':
                return button
        raise CannotFindElementError('no Next button?')

    @property
    def final_registration_button(self):
        """Returns the final Registration button."""
        buttons = self.selenium.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == 'Register':
                return button
        raise CannotFindElementError('no Register button?')

    @property
    def participation_level_radio_buttons(self):
        """Returns the participation level radio buttons."""
        input_buttons = self.selenium.find_elements_by_tag_name('input')
        radio_buttons = [ib for ib in input_buttons
                         if ib.get_attribute('type') == 'radio']
        return radio_buttons

    @property
    def participation_level_participant_radio_button(self):
        """Returns the radio button that indicates 'Participant'."""
        for radio_button in self.payment_options_radio_buttons:
            if radio_button.get_attribute("value") == "participant":
                return radio_button
        raise CannotFindElementError('no Participant radio button?')

    @property
    def participation_level_respondent_radio_button(self):
        """Returns the radio button that indicates 'Survey Respondent'."""
        for radio_button in self.payment_options_radio_buttons:
            if radio_button.get_attribute("value") == "respondent":
                return radio_button
        raise CannotFindElementError('no Survey Respondent radio button?')

    @property
    def payment_options_radio_buttons(self):
        """Returns the payment options radio buttons."""
        input_buttons = self.selenium.find_elements_by_tag_name('input')
        radio_buttons = [ib for ib in input_buttons
                         if ib.get_attribute('type') == 'radio']
        return radio_buttons

    @property
    def pay_now_radio_button(self):
        """Returns the radio button that indicates 'Pay now please'."""
        for radio_button in self.payment_options_radio_buttons:
            if radio_button.get_attribute('value') == Subscription.PAY_NOW:
                return radio_button
        raise CannotFindElementError('no Pay Now radio button?')

    @property
    def pay_later_radio_button(self):
        """Returns the radio button that indicates 'Pay later please'."""
        for radio_button in self.payment_options_radio_buttons:
            if radio_button.get_attribute('value') == Subscription.PAY_LATER:
                return radio_button
        raise CannotFindElementError('no Pay Later radio button?')

    def get_text_input_element(self, end_of_id):
        text_input_elements = self.get_input_elements(type="text")
        for text_input_element in text_input_elements:
            if text_input_element.get_attribute("id").endswith(end_of_id):
                return text_input_element
        raise CannotFindElementError(
            "no {0} element?".format(end_of_id.replace("_",
                                                       " ")))

    @property
    def credit_card_number_element(self):
        credit_card_number_element = self.get_text_input_element(
            "card_number")
        return credit_card_number_element

    @property
    def credit_card_expiration_month_element(self):
        credit_card_expiration_month_element = self.get_text_input_element(
            "exp_month")
        return credit_card_expiration_month_element

    @property
    def credit_card_expiration_year_element(self):
        credit_card_expiration_year_element = self.get_text_input_element(
            "exp_year")
        return credit_card_expiration_year_element

    @property
    def credit_card_number(self):
        return self.credit_card_number_element.text

    @credit_card_number.setter
    def credit_card_number(self, value):
        self.credit_card_number_element.clear()
        self.credit_card_number_element.send_keys(value)

    @property
    def credit_card_expiration_month(self):
        return self.credit_card_expiration_month_element.text

    @credit_card_expiration_month.setter
    def credit_card_expiration_month(self, value):
        self.credit_card_expiration_month_element.clear()
        self.credit_card_expiration_month_element.send_keys(value)

    @property
    def credit_card_expiration_year(self):
        return self.credit_card_expiration_year_element.text

    @credit_card_expiration_year.setter
    def credit_card_expiration_year(self, value):
        self.credit_card_expiration_year_element.clear()
        self.credit_card_expiration_year_element.send_keys(value)

    def get_input_elements(self, type):
        input_elements = self.selenium.find_elements_by_tag_name('input')
        type_elements = [ib for ib in input_elements
                         if ib.get_attribute("type") == type]
        return type_elements

    def summon_the_wizard(self):
        self.selenium.get('/'.join((self.live_server_url,
                                    "register")))

    def select_school(self, school=None):
        """Picks an school, then moves along."""
        self.selected_school = school or self.school
        self.next_button.click()

    @property
    def select_school_select_element(self):
        web_element = self.patiently_find(look_for='school_select',
                                          by=By.ID)
        select = Select(web_element)
        return select

    @property
    def selected_school(self):
        select_element = self.select_school_select_element
        selected_option = select_element.first_selected_option
        return selected_option.get_attribute('value')

    @selected_school.setter
    def selected_school(self, school):
        select_element = self.select_school_select_element
        select_element.select_by_value(str(school.account_num))

    def current_page_is_tool_summary_page(self):
        self.wait()
        tool_summary_path = reverse(
            'tool-summary',
            kwargs={'institution_slug': self.institution.slug})
        current_url_path = urlparse.urlparse(self.selenium.current_url).path
        return tool_summary_path == current_url_path

    def current_page_is_final_confirmation_page(self):
        self.wait()
        try:
            self.final_registration_button
        except CannotFindElementError as ex:
            self.fail(ex.message)
        else:
            return True

    def test_registered_folks_are_redirected_to_tool_summary(self):
        """Are insts already registered redirected to the tool summary page?"""
        self.institution.aashe_id = self.school.account_num
        self.institution.save()
        self.select_school()
        self.assertTrue(self.current_page_is_tool_summary_page())

    def test_unregistered_folks_are_redirected_to_participation_level_page(
            self):
        """Are insts not registered redirected to the participation level page?
        """
        self.select_school()
        self.assertIsNotNone(self.participation_level_radio_buttons)

    def test_participant_asked_for_exec_contact_info(self):
        """Are participants asked for executive contact info?"""
        # Pick an school:
        self.select_school()
        # Participation level page:
        self.participation_level = PARTICIPANT
        # Contact info page:
        try:
            self.get_text_input_element(
                end_of_id='executive_contact_first_name')
        except CannotFindElementError as ex:
            self.fail(ex.message)

    def test_respondents_not_asked_for_exec_contact_info(self):
        """Are respondents not asked for executive contact info?"""
        self.select_school()
        # Participation level page:
        self.participation_level = RESPONDENT
        # Contact info page:
        self.assertTrue(self.current_page_is_contact_info_page())
        with self.assertRaises(CannotFindElementError):
            self.get_text_input_element(
                end_of_id='executive_contact_first_name')

    def current_page_is_contact_info_page(self):
        try:
            self.get_text_input_element(end_of_id='contact_first_name')
        except CannotFindElementError:
            return False
        else:
            return True

    def _enter_contact_info(self, contact_info):
        for key, value in contact_info.items():
            element = self.get_text_input_element(end_of_id=key)
            self.type(element=element, value=value)

    def enter_contact_info(self):
        contact_info = {'contact_first_name': 'Jimmy',
                        'contact_last_name': 'Jonesy',
                        'contact_title': 'Humble Servant',
                        'contact_department': 'Refreshments',
                        'contact_phone': '1231231234',
                        'contact_email': 'jimmy@jonestown.gy'}
        self._enter_contact_info(contact_info=contact_info)

    def enter_executive_contact_info(self):
        executive_contact_info = {
            'executive_contact_first_name': 'Jackie',
            'executive_contact_last_name': 'Mercer',
            'executive_contact_title': 'Master Blaster',
            'executive_contact_department': 'Combustibles',
            'executive_contact_email': 'haha@mercer.nom'}
        self._enter_contact_info(contact_info=executive_contact_info)

    def test_respondents_skip_subscription_steps(self):
        """Are the suscription steps skipped for respondents?"""
        self.select_school()
        self.participation_level_respondent_radio_button.click()
        self.next_button.click()
        self.assertTrue(self.current_page_is_final_confirmation_page())

    def _test_no_amount_due_skips_payment_steps(self, pay_when):
        """Are payment steps skipped if amount due is 0?

        `pay_when` - now or later
        """
        self.assertTrue(pay_when in [NOW, LATER])

        # select school page:
        self.select_school()

        # particiapation level page:
        self.participation_level = PARTICIPANT

        # contact info page:
        self.enter_contact_info()
        self.enter_executive_contact_info()
        self.next_button.click()

        # subscription price page:
        self.promo_code = self.freebie_code.code
        self.apply_promo_code_button.click()
        self.next_button.click()

        # should be on final confirmation page now:
        self.assertTrue(self.current_page_is_final_confirmation_page())

    def test_pay_now_no_amount_due_skips_payment_steps(self):
        """Are payment steps skipped if choosing to pay now & amount due is 0?
        """
        self._test_no_amount_due_skips_payment_steps(pay_when='now')

    def test_pay_later_no_amount_due_skips_payment_steps(self):
        """Payment steps skipped if choosing to pay later & amount due is 0?
        """
        self._test_no_amount_due_skips_payment_steps(pay_when='later')

    @property
    def participation_level(self):
        if self.participation_level_participant_radio_button.is_selected():
            return PARTICIPANT
        elif self.participation_level_respondent_radio_button.is_selected():
            return RESPONDENT
        else:
            return None

    @participation_level.setter
    def participation_level(self, value):
        self.assertIn(value, [PARTICIPANT, RESPONDENT])
        if value == PARTICIPANT:
            button = self.participation_level_participant_radio_button
        else:
            button = self.participation_level_respondent_radio_button
        button.click()
        self.next_button.click()

    @property
    def payment_option(self):
        if self.pay_now_radio_button.is_selected():
            return NOW
        elif self.pay_later_radio_button.is_selected():
            return LATER
        else:
            return None

    @payment_option.setter
    def payment_option(self, value):
        self.assertIn(value, [NOW, LATER])
        if value == NOW:
            button = self.pay_now_radio_button
        else:
            button = self.pay_later_radio_button
        button.click()
        self.next_button.click()

    def current_page_is_credit_card_details_page(self):
        return self.credit_card_number_element.is_displayed()

    def test_pay_now_leads_to_credit_card_info_page(self):
        """After choosing 'Pay Now', is the credit card info page shown?"""
        # Select school page:
        self.select_school()
        # Participation level page:
        self.participation_level = PARTICIPANT
        # Contact info page:
        self.enter_contact_info()
        self.enter_executive_contact_info()
        self.next_button.click()
        # Subscription price page:
        self.next_button.click()
        # Payment options page:
        self.payment_option = NOW
        # Should be on credit card details page now:
        self.assertTrue(self.current_page_is_credit_card_details_page())

    def test_pay_later_skips_credit_card_info_page(self):
        """After choosing 'Pay Later', is the final confirmation page shown?
        """
        self.select_school()
        # Participation level page:
        self.participation_level = PARTICIPANT
        # Contact info page:
        self.enter_contact_info()
        self.enter_executive_contact_info()
        self.next_button.click()
        # Subscription price page:
        self.next_button.click()
        # Payment options page:
        self.payment_option = LATER
        # Should be on credit card details page now:
        self.assertTrue(self.current_page_is_final_confirmation_page())
