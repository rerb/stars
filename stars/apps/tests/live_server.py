"""
    Base LiveServerTestCase customized for STARS tests.
"""
from django import test
from selenium.webdriver.firefox import webdriver

from stars.test_factories import (InstitutionFactory, StarsAccountFactory,
                                  UserFactory)


class StarsLiveServerTest(test.LiveServerTestCase):
    """
        Base test case that:

          - takes care of starting and stopping a webdriver;
          - creates a Institution and an admin User for that Institution;
          - logs the user in;
          - provides helper functions (like go_to_reporting_tool()).
    """
    @classmethod
    def setUpClass(cls):
        cls.selenium = webdriver.WebDriver()
        super(StarsLiveServerTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(StarsLiveServerTest, cls).tearDownClass()

    def setUp(self):
        self.plain_text_password = 'password'
        self.user = UserFactory(username='username',
                                password=self.plain_text_password)
        self.institution = InstitutionFactory()
        self.stars_account = StarsAccountFactory(user=self.user,
                                                 institution=self.institution,
                                                 user_level='admin')
        self.login()

    def login(self):
        self.selenium.get(self.live_server_url)

        # Login:
        log_in_link = self.selenium.find_element_by_link_text('Log In')
        log_in_link.click()

        username_input = self.selenium.find_element_by_id('id_username')
        username_input.send_keys(self.user.username)

        password_input = self.selenium.find_element_by_id('id_password')
        password_input.send_keys(self.plain_text_password)

        login_button = self.selenium.find_element_by_css_selector(
            'button.btn.btn-primary')
        login_button.click()

        # Terms of Service page:
        tos_checkbox = self.selenium.find_element_by_id('id_terms_of_service')
        tos_checkbox.click()

        tos_submit_button = self.selenium.find_element_by_css_selector(
            'button[type="submit"]')
        tos_submit_button.click()

    def go_to_reporting_tool(self):
        reporting_tool_tab = self.selenium.find_element_by_link_text(
            'Reporting')
        reporting_tool_tab.click()
