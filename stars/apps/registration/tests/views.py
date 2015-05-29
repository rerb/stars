from logging import getLogger, CRITICAL
import urlparse

from django.core import mail
from django.core.urlresolvers import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import TimeoutException
import mock

from stars.apps.institutions.models import (Institution,
                                            StarsAccount,
                                            Subscription,
                                            SubscriptionPayment)
from stars.apps.institutions.tests.subscription import GOOD_CREDIT_CARD
from stars.apps.submissions.models import SubmissionSet
from stars.apps.tests.live_server import StarsLiveServerTest
from stars.apps.tool.tests.views import InstitutionAdminToolMixinTest
from stars.test_factories import (OrganizationFactory,
                                  ValueDiscountFactory)

from .. import views

PARTICIPANT = 'participant'
RESPONDENT = 'respondent'

LATER = 'later'
NOW = 'now'

CONTACT_INFO = {'contact_first_name': u'Jimmy',
                'contact_last_name': u'Jonesy',
                'contact_title': u'Humble Servant',
                'contact_department': u'Refreshments',
                'contact_phone': u'123-123-1234',
                'contact_email': u'jimmy@jonestown.gy'}

EXECUTIVE_CONTACT_INFO = {
    'executive_contact_first_name': u'Jackie',
    'executive_contact_last_name': u'Mercer',
    'executive_contact_title': u'Master Blaster',
    'executive_contact_department': u'Combustibles',
    'executive_contact_email': u'haha@mercer.nom'}

# Don't bother me:
logger = getLogger('stars')
logger.setLevel(CRITICAL)


class CannotFindElementError(Exception):
    pass


class ForcedException(Exception):
    pass


class RegistrationWizardLiveServerTest(StarsLiveServerTest):

    # TODO: need all these fixtures?  any of these?
    # NOTE: need old_cms_test_data.json, for sure, at least now.
    fixtures = [
        'registration_tests.json',
        'notification_emailtemplate_tests.json',
        'old_cms_test_data.json']

    def setUp(self, *args, **kwargs):
        super(RegistrationWizardLiveServerTest, self).setUp(*args, **kwargs)
        self.institution.aashe_id = None  # not registered for STARS
        self.institution.save()
        self.school = self.school_factory(summon_the_wizard=False)
        self.freebie_code = ValueDiscountFactory(amount=0,
                                                 percentage=100)
        self._previous_register_args = {}
        self._participation_level = None
        self.summon_the_wizard()

    def school_factory(self, summon_the_wizard=True):
        """Return a new school Organization.

        `summon_the_wizard` is a euphemism for refreshing
        the list of schools.
        """
        school = OrganizationFactory(org_type="Four Year Institution",
                                     country="United States of America")
        if summon_the_wizard:
            self.summon_the_wizard()
        return school

    # participation level:
    @property
    def participation_level(self):
        return self._participation_level

    @participation_level.setter
    def participation_level(self, value):
        self.assertIn(value, [PARTICIPANT, RESPONDENT])
        self._participation_level = value
        if value == PARTICIPANT:
            button = self.get_register_button('full-access')
        else:
            button = self.get_register_button('basic-access')
        button.click()

    # Buttons;
    # - a few helper functions, and;
    # - one property for each button element:
    def get_button_with_text(self, text):
        buttons = self.selenium.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == text:
                return button
        raise CannotFindElementError('no {text} button?'.format(
            text=text))

    def get_register_buttons(self):
        return self.selenium.find_elements_by_partial_link_text('Register')

    def get_register_button(self, access_level):
        for register_button in self.get_register_buttons():
            if access_level in register_button.get_attribute('href'):
                return register_button
        raise CannotFindElementError(
            'no register for {access_level} button?'.format(
                access_level=access_level))

    @property
    def register_full_access_button(self):
        """Returns the Register for Full Access button."""
        self.get_register_button('full-access')

    @property
    def register_basic_access_button(self):
        """Returns the Register for Basic Access button."""
        self.get_register_button('basic-access')

    @property
    def apply_promo_code_button(self):
        """Returns the Apply Promo Code button."""
        apply_promo_code_button = self.patiently_find(
            look_for='apply-promo-code-button', by=By.ID)
        return apply_promo_code_button

    @property
    def final_registration_button(self):
        """Returns the final Registration button."""
        buttons = self.selenium.find_elements_by_tag_name('button')
        # There are 2 'Register' submit buttons on the form, we want
        # the last one, so we reverse the list and take the first:
        buttons.reverse()
        for button in buttons:
            if (button.text == 'Register' and
                button.get_attribute('type') == 'submit'):
                return button
        raise CannotFindElementError('no final registration button?')

    @property
    def next_button(self):
        """Returns the Next button."""
        return self.get_button_with_text('Next')

    # Input elements;
    # - two helper functions;
    # - one property for the input element;
    # - one property for the value of the input field, and;
    # - a property setter for the input field.
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

    # promo code:
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

    # selected_school:
    @property
    def selected_school_select_element(self):
        web_element = self.patiently_find(look_for='school_select',
                                          by=By.ID)
        select = Select(web_element)
        return select

    @property
    def selected_school(self):
        select_element = self.selected_school_select_element
        selected_option = select_element.first_selected_option
        return selected_option.get_attribute('value')

    @selected_school.setter
    def selected_school(self, school):
        select_element = self.selected_school_select_element
        select_element.select_by_value(str(school.account_num))

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

    # Sometimes we just want to know if the current page is the
    # one we expected:
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

    def current_page_is_contact_info_page(self):
        try:
            self.get_text_input_element(end_of_id='contact_first_name')
        except CannotFindElementError:
            return False
        else:
            return True

    def current_page_is_credit_card_details_page(self):
        return self.credit_card_number_element.is_displayed()

    def current_page_is_survey_page(self):
        return 'survey' in self.selenium.title.lower()

    def summon_the_wizard(self):
        self.selenium.get('/'.join(
            (self.live_server_url,
             "pages/participate/register-stars.html")))

    def select_school(self, school=None):
        """Picks an school, then moves along."""
        self.selected_school = school or self.school
        self.school = school or self.school
        self.next_button.click()

    def _enter_contact_info(self, contact_info):
        for key, value in contact_info.items():
            element = self.get_text_input_element(end_of_id=key)
            self.type(element=element, value=value)

    def enter_contact_info(self):
        self._enter_contact_info(contact_info=CONTACT_INFO)

    def enter_executive_contact_info(self):
        self._enter_contact_info(contact_info=EXECUTIVE_CONTACT_INFO)

    def submit_contact_info(self, participation_level):
        """Enters contact info, then submits the contact info form."""
        self.assertIn(participation_level, [PARTICIPANT, RESPONDENT])
        self.enter_contact_info()
        self.enter_executive_contact_info()
        if participation_level == PARTICIPANT:
            self.next_button.click()
        else:
            self.final_registration_button.click()

    ##########
    # TESTS! #
    ##########
    def test_registered_folks_are_redirected_to_tool_summary(self):
        """Are insts already registered redirected to the tool summary page?"""
        self.institution.aashe_id = self.school.account_num
        self.institution.save()
        self.participation_level = PARTICIPANT
        self.select_school()
        self.assertTrue(self.current_page_is_tool_summary_page())

    def test_unregistered_folks_are_redirected_to_contact_info_page(self):
        """Are insts not registered redirected to the contact info page?
        """
        self.participation_level = PARTICIPANT
        self.select_school()
        self.assertTrue(self.current_page_is_contact_info_page())

    def test_respondents_skip_subscription_steps(self):
        """Are the suscription steps skipped for respondents?"""
        self.participation_level = RESPONDENT
        self.select_school()
        self.assertTrue(self.current_page_is_final_confirmation_page())

    def test_nonmember_sees_please_join_us_message_on_price_form(self):
        """Do non member institutions see the Please Join AASHE! message
        on the price form?"""
        self.school.is_member = False
        self.school.save()
        self.participation_level = PARTICIPANT
        self.select_school(school=self.school)
        self.submit_contact_info(participation_level=PARTICIPANT)
        nonmember_message = self.patiently_find(
            look_for='message-for-nonmembers', by=By.ID)
        self.assertIsNotNone(nonmember_message)

    def test_member_does_not_see_please_join_us_message_on_price_form(self):
        """Do member institutions see the Please Join AASHE! message
        on the price form?"""
        self.school.is_member = True
        self.school.save()
        self.participation_level = PARTICIPANT
        self.select_school(school=self.school)
        self.submit_contact_info(participation_level=PARTICIPANT)
        with self.assertRaises(TimeoutException):
            self.patiently_find(look_for='message-for-nonmembers',
                                by=By.ID)

    def _test_no_amount_due_skips_payment_steps(self, pay_when):
        """Are payment steps skipped if amount due is 0?

        `pay_when` - now or later
        """
        self.assertTrue(pay_when in [NOW, LATER])

        # participation level page:
        self.participation_level = PARTICIPANT

        # select school page:
        self.select_school()

        # contact info page:
        self.submit_contact_info(participation_level=PARTICIPANT)

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

    def test_pay_now_leads_to_credit_card_info_page(self):
        """After choosing 'Pay Now', is the credit card info page shown?"""
        # Participation level page:
        self.participation_level = PARTICIPANT
        # Select school page:
        self.select_school()
        # Contact info page:
        self.submit_contact_info(participation_level=PARTICIPANT)
        # Subscription price page:
        self.next_button.click()
        # Payment options page:
        self.payment_option = NOW
        # Should be on credit card details page now:
        self.assertTrue(self.current_page_is_credit_card_details_page())

    def test_pay_later_skips_credit_card_info_page(self):
        """After choosing 'Pay Later', is the final confirmation page shown?
        """
        self.participation_level = PARTICIPANT
        self.select_school()
        # Contact info page:
        self.submit_contact_info(participation_level=PARTICIPANT)
        # Subscription price page:
        self.next_button.click()
        # Payment options page:
        self.payment_option = LATER
        # Should be on credit card details page now:
        self.assertTrue(self.current_page_is_final_confirmation_page())

    def test_participant_finally_redirected_to_survey(self):
        self.register(participation_level=PARTICIPANT,
                      payment_option=LATER)
        self.current_page_is_survey_page()

    def test_respondent_finally_redirected_to_survey(self):
        self.register(participation_level=RESPONDENT)
        self.current_page_is_survey_page()

    #############################################
    # tests that database is updated correctly: #
    #############################################
    def register(self,
                 participation_level,
                 school=None,
                 payment_option=None,
                 new_registration=True):
        """For testing the side effects of a successful invocation
        of the wizard.

        Call register(), assume it succeeds, and then start poking around.

        When `new_registration` is False, and the other args match
        the args of the previous invocation of this method, the
        registration process is short-circuited, and doesn't really
        happen.  Useful for testing the after effects of a registration
        separately; e.g., number of emails sent, if subscription was
        created, etc.  Allows for individual tests (one assert per
        test), without the overhead of registering before each one.
        """
        def args_dict():
            """Returns a dictionary of the arguments used to see if
            this instance of register() was called with the same args
            as the previous.

            Essentially, that's all args except `new_registration`.
            """
            return {
                'participation_level': participation_level,
                'school': school,
                'payment_option': payment_option
            }

        def _register():
            self.participation_level = participation_level

            self.select_school(school=school)

            self.submit_contact_info(participation_level=participation_level)

            if participation_level == PARTICIPANT:
                self.next_button.click()  # on price page.
                self.payment_option = payment_option
                if payment_option == NOW:
                    self.credit_card_number = GOOD_CREDIT_CARD
                    self.credit_card_expiration_month = "12"
                    self.credit_card_expiration_year = "2020"
                self.final_registration_button.click()

        self.assertIn(participation_level, [PARTICIPANT, RESPONDENT])
        self.assertIn(payment_option, [LATER, NOW, None])

        self._register_args = args_dict()

        school = school or self.school

        if (new_registration or
            self._register_args != self._previous_register_args):

            try:
                _register()
            except Exception as exc:
                self._previous_register_args = {}
                raise exc

        # remember args in case next call wants to reuse this registration:
        self._previous_register_args = self._register_args

    def _test_registration_model_mutation(self,
                                          participation_level,
                                          model,
                                          difference,
                                          school=None,
                                          payment_option=None):
        """
        _test_registration_model_mutation(participation_level=PARTICIPANT,
                                          model=Subscription,
                                          difference=1,
                                          school=OrganizationFactory(),
                                          payment_option=NOW)

        is True if after a participant paying now registers,
        there's one more Subscription.
        """
        initial_count = model.objects.count()
        self.register(participation_level=participation_level,
                      school=school,
                      payment_option=payment_option)
        return initial_count + difference == model.objects.count()

    def _test_registration_updates_contact_info(self, contact_info):
        # clear the contact info from the Institution:
        school = self.school_factory()

        for contact_field in contact_info.keys():
            setattr(self.institution, contact_field, '')
        self.institution.save()

        self.register(participation_level=PARTICIPANT,
                      school=school,
                      payment_option=LATER,
                      new_registration=True)

        institution = Institution.objects.get(aashe_id=school.account_num)
        contact_info_from_institution = {}

        for contact_field in contact_info.keys():
            contact_info_from_institution[contact_field] = (
                getattr(institution, contact_field))

        self.assertDictEqual(contact_info_from_institution, contact_info)

    def test_registration_updates_institution_contact_info(self):
        self._test_registration_updates_contact_info(CONTACT_INFO)

    def test_registration_updates_institution_executive_contact_info(self):
        self.maxDiff = None
        self._test_registration_updates_contact_info(EXECUTIVE_CONTACT_INFO)

    #############################
    # full access pay now tests #
    #############################
    def test_participant_paying_now_creates_institution(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=PARTICIPANT,
                model=Institution,
                difference=(+1),
                school=self.school_factory(),
                payment_option=NOW))

    def test_participant_paying_now_creates_subscription(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=PARTICIPANT,
                model=Subscription,
                difference=(+1),
                school=self.school_factory(),
                payment_option=NOW))

    def test_participant_paying_now_creates_stars_account(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=PARTICIPANT,
                model=StarsAccount,
                difference=(+1),
                school=self.school_factory(),
                payment_option=NOW))

    def test_participant_paying_now_creates_subscription_payment(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=PARTICIPANT,
                model=SubscriptionPayment,
                difference=(+1),
                school=self.school_factory(),
                payment_option=NOW))

    def test_participant_paying_now_creates_subsmissionset(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=PARTICIPANT,
                model=SubmissionSet,
                difference=(+1),
                school=self.school_factory(),
                payment_option=NOW))

    def test_participant_paying_now_sets_institution_current_submission(self):
        self.institution.current_submission = None
        self.institution.save()
        school = self.school_factory()
        self.register(participation_level=PARTICIPANT,
                      school=school,
                      payment_option=NOW,
                      new_registration=True)
        self.assertIsNotNone(self.school)

    def test_emails_sent_for_full_access_paying_now(self):
        initial_num_outbound_mails = len(mail.outbox)

        self.register(participation_level=PARTICIPANT,
                      payment_option=LATER)

        self.assertEqual(len(mail.outbox),
                         initial_num_outbound_mails + 2)

        self.assertItemsEqual(
            mail.outbox[0].to,
            [EXECUTIVE_CONTACT_INFO['executive_contact_email']])

        self.assertItemsEqual(
            mail.outbox[1].to,
            [CONTACT_INFO['contact_email'], self.user.email])

    ###############################
    # full access pay later tests #
    ###############################
    def test_participant_paying_later_creates_institution(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=PARTICIPANT,
                model=Institution,
                difference=(+1),
                school=self.school_factory(),
                payment_option=LATER))

    def test_participant_paying_later_creates_subscription(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=PARTICIPANT,
                model=Subscription,
                difference=(+1),
                school=self.school_factory(),
                payment_option=LATER))

    def test_participant_paying_later_creates_stars_account(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=PARTICIPANT,
                model=StarsAccount,
                difference=(+1),
                school=self.school_factory(),
                payment_option=LATER))

    def test_participant_paying_later_creates_submissionset(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=PARTICIPANT,
                model=SubmissionSet,
                difference=(+1),
                school=self.school_factory(),
                payment_option=LATER))

    def test_participant_paying_later_does_not_create_subscription_payment(
            self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=PARTICIPANT,
                model=SubscriptionPayment,
                difference=(+0),
                school=self.school_factory(),
                payment_option=LATER))

    def test_participant_paying_later_sets_institution_current_submission(
            self):
        self.institution.current_submission = None
        self.institution.save()
        school = self.school_factory()
        self.register(participation_level=PARTICIPANT,
                      school=school,
                      payment_option=NOW,
                      new_registration=True)
        self.assertIsNotNone(self.school)

    def test_emails_sent_for_full_access_paying_later(self):
        initial_num_outbound_mails = len(mail.outbox)

        self.register(participation_level=PARTICIPANT,
                      payment_option=LATER)

        self.assertEqual(len(mail.outbox),
                         initial_num_outbound_mails + 2)

        self.assertItemsEqual(
            mail.outbox[0].to,
            [EXECUTIVE_CONTACT_INFO['executive_contact_email']])

        self.assertItemsEqual(
            mail.outbox[1].to,
            [CONTACT_INFO['contact_email'], self.user.email])

    ######################
    # basic access tests #
    ######################
    def test_basic_access_registration_creates_institution(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=RESPONDENT,
                model=Institution,
                difference=(+1),
                school=self.school_factory()))

    def test_basic_access_registration_creates_stars_account(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=RESPONDENT,
                model=StarsAccount,
                difference=(+1),
                school=self.school_factory()))

    def test_basic_access_registration_creates_submissionset(self):
        self.assertTrue(
            self._test_registration_model_mutation(
                participation_level=RESPONDENT,
                model=SubmissionSet,
                difference=(+1),
                school=self.school_factory()))

    def test_no_emails_sent_for_basic_access_registration(self):
        """Are any emails sent for Basic Access registration?"""
        initial_num_outbound_mails = len(mail.outbox)

        self.register(participation_level=RESPONDENT,
                      new_registration=False)

        self.assertEqual(len(mail.outbox), initial_num_outbound_mails)

    ###################################################
    # tests of exception handling (i.e., cleaning up) #
    ###################################################
    def _set_initial_object_counts(self):
        self.initial_institutions = Institution.objects.count()
        self.initial_starsaccounts = StarsAccount.objects.count()
        self.initial_submissionsets = SubmissionSet.objects.count()
        self.initial_subscriptions = Subscription.objects.count()
        self.initial_payments = SubscriptionPayment.objects.count()

    def _initial_object_counts_are_still_correct(self):
        self.assertEqual(self.initial_institutions,
                         Institution.objects.count())
        self.assertEqual(self.initial_starsaccounts,
                         StarsAccount.objects.count())
        self.assertEqual(self.initial_submissionsets,
                         SubmissionSet.objects.count())
        self.assertEqual(self.initial_subscriptions,
                         Subscription.objects.count())
        self.assertEqual(self.initial_payments,
                         SubscriptionPayment.objects.count())

    def test_invalid_cc_tx_doesnt_create_records(self):
        """Is the db left untouched when a credit card transaction fails?"""
        self._set_initial_object_counts()

        self.participation_level = PARTICIPANT
        self.select_school()
        self.submit_contact_info(participation_level=PARTICIPANT)
        self.next_button.click()  # price page
        self.payment_option = NOW
        self.credit_card_number = "badcreditcardnumber"
        self.credit_card_expiration_month = "12"
        self.credit_card_expiration_year = "2020"
        self.final_registration_button.click()

        self._initial_object_counts_are_still_correct()

    def _raise_forced_exception(*args, **kwargs):
        """Stub to raise an exception, for testing exception handling."""
        raise ForcedException()

    @mock.patch('stars.apps.registration.views.init_starsaccount',
                _raise_forced_exception)
    def test_cleanup_for_basic_access_broken_init_starsaccount(self):
        """If init_starsaccount fails for Basic Access, is mess cleaned up?
        """
        self._set_initial_object_counts()
        self.register(participation_level=RESPONDENT,
                      new_registration=True)
        self._initial_object_counts_are_still_correct()

    @mock.patch('stars.apps.registration.views.init_starsaccount',
                _raise_forced_exception)
    def test_cleanup_for_full_access_broken_init_starsaccount(self):
        """If init_starsaccount fails for Full Access, is the mess cleaned up?
        """
        self._set_initial_object_counts()
        self.register(participation_level=PARTICIPANT,
                      payment_option=Subscription.PAY_LATER,
                      new_registration=True)
        self._initial_object_counts_are_still_correct()

    @mock.patch('stars.apps.registration.views.init_submissionset',
                _raise_forced_exception)
    def test_cleanup_for_basic_access_broken_init_submissionset(self):
        """If init_submissionset fails for Basic Access, is mess cleaned up?
        """
        self._set_initial_object_counts()
        self.register(participation_level=RESPONDENT,
                      new_registration=True)
        self._initial_object_counts_are_still_correct()

    @mock.patch('stars.apps.registration.views.init_submissionset',
                _raise_forced_exception)
    def test_cleanup_for_full_access_broken_init_submissionset(self):
        """If init_submissionset fails for Full Access, is the mess cleaned up?
        """
        self._set_initial_object_counts()
        self.register(participation_level=PARTICIPANT,
                      payment_option=Subscription.PAY_LATER,
                      new_registration=True)
        self._initial_object_counts_are_still_correct()


class SurveyViewTest(InstitutionAdminToolMixinTest):

    view_class = views.SurveyView
