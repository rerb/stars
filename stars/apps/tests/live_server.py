"""
    Base LiveServerTestCase customized for STARS tests.
"""
from django import test
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

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

    def patiently_find(self, look_for, by=By.ID, wait_for=10):
        """Find an element, only timing out after `wait_for` seconds.

        `look_for` is the element identifier, and `by` is the type
        of search to perform.
        """
        result = WebDriverWait(self.selenium, wait_for).until(
            expected_conditions.presence_of_element_located((by, look_for)))
        return result

    def login(self):
        self.selenium.get(self.live_server_url)

        # Login:
        log_in_link = self.patiently_find(look_for='Log In', by=By.LINK_TEXT)
        log_in_link.click()

        username_input = self.patiently_find(look_for='id_username',
                                             by=By.ID)
        username_input.send_keys(self.user.username)

        password_input = self.selenium.find_element_by_id('id_password')
        password_input.send_keys(self.plain_text_password)

        login_button = self.selenium.find_element_by_css_selector(
            'button.btn.btn-primary')
        login_button.click()

    def go_to_reporting_tool(self):
        reporting_tool_tab = self.patiently_find(look_for='Reporting',
                                                 by=By.LINK_TEXT)
        reporting_tool_tab.click()
