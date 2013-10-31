"""
    Base LiveServerTestCase customized for STARS tests.
"""
import collections
import os
import sys
import unittest

import django
from selenium.webdriver import chrome
from selenium.webdriver import firefox
from selenium.webdriver import phantomjs
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import TimeoutException

from stars.test_factories import (InstitutionFactory, StarsAccountFactory,
                                  UserFactory)


class NoWebdriverForPlatformError(Exception):
    pass


Browser = collections.namedtuple(
    'Browser',
    ['platform',  # as returned by sys.platform
     'name',
     'sentinels', # list of files that, when present, indicate the browser
                  # is installed
     'implementation'  # the webdriver implementation
 ])


WEBDRIVERS = [Browser(platform='darwin',
                      name='phantomjs',
                      sentinels=['/usr/local/bin/phantomjs'],
                      implementation=phantomjs.webdriver),
              Browser(platform='darwin',
                      name='firefox',
                      sentinels=['/Applications/Firefox.app'],
                      implementation=firefox.webdriver),
              Browser(platform='darwin',
                      name='chrome',
                      sentinels=['/Applications/Google Chrome.app',
                       '/usr/local/bin/chromedriver'],
                      implementation=chrome.webdriver),
              #TODO: test on linux . . . 
              Browser(platform='linux2',
                      name='firefox',
                      sentinels=['/usr/bin/firefox'],
                      implementation=firefox.webdriver),
              Browser(platform='linux2',
                      name='chrome', 
                      sentinels=['/usr/bin/chromium-browser'],
                      implementation=chrome.webdriver),
              Browser(platform='linux2',
                      name='phantomjs',
                      sentinels=['/usr/bin/phantomjs'],
                      implementation=phantomjs.webdriver)]


def skip_live_server_tests():
    return '--liveserver=' in sys.argv


class LiveServerTestCase(django.test.LiveServerTestCase):
    """
    A test.LiveServerTestCase that handles the webdriver implementation
    used.  Picks one from WEBDRIVERS, instantiates it, and quits it
    in tearDownClass().

    So, for instance, we don't specify a specific implementation that
    isn't installed on the test machine, and then are mystified by
    the resulting error.
    """
    @classmethod
    def setUpClass(cls):
        if not skip_live_server_tests():
            super(LiveServerTestCase, cls).setUpClass()
            webdriver = cls.get_webdriver()
            cls.selenium = webdriver.WebDriver()

    @classmethod
    def tearDownClass(cls):
        if not skip_live_server_tests():
            cls.selenium.quit()
            super(LiveServerTestCase, cls).tearDownClass()

    @classmethod
    def get_webdriver(cls):
        """Returns a webdriver implementation appropriate for this
        sys.platform.  Looks through WEBDRIVERS, in order, and returns
        the first it finds that's installed."""
        for webdriver in [implementation for implementation in WEBDRIVERS
                          if implementation.platform == sys.platform]:
            for sentinel in webdriver.sentinels:
                try:
                    os.stat(sentinel)
                except OSError as e:
                    print 'cannot stat', sentinel, ': ', e
                else:
                    return webdriver.implementation
        raise NoWebdriverForPlatformError(sys.platform)

    def runTest(self):
        """Need runTest() so we can instantiate LiveServerTestCase
        itself.  For, like, testing and stuff.
        """
        pass


class StarsLiveServerTest(LiveServerTestCase):
    """Base test case that:

          - takes care of starting and stopping a webdriver;
          - creates a Institution and an admin User for that Institution;
          - logs the user in;
          - provides helper functions (like go_to_reporting_tool());
          - is skipped if the argument '--liveserver=' is provided on
            the command line.

       Skipping is more efficiently done by raising
       unittest.SkipTest() in setUpClass, but then the number of tests
       skipped is reported as 1, regardless of how many subclassed
       tests are actually skipped.  The tests of
       skip_live_server_tests() in setUpClass(), tearDownClass(), and
       setUp() allow for skipping, while preserving the number of
       skips.
    """
    @classmethod
    def setUpClass(cls):
        if not skip_live_server_tests():
            super(StarsLiveServerTest, cls).setUpClass()
            cls.logged_in = False

    def setUp(self):
        if skip_live_server_tests():
            raise unittest.SkipTest()
        super(StarsLiveServerTest, self).setUp()
        self.plain_text_password = 'password'
        self.user = UserFactory(username='username',
                                password=self.plain_text_password)
        self.institution = InstitutionFactory()
        self.stars_account = StarsAccountFactory(user=self.user,
                                                 institution=self.institution,
                                                 user_level='admin')
        self.login()

    def patiently_find(self, look_for, by=By.ID, timeout=10):
        """Find an element, only timing out after `timeout` seconds.

        `look_for` is the element identifier, and `by` is the type
        of search to perform.
        """
        try:
            result = WebDriverWait(self.selenium, timeout).until(
                expected_conditions.presence_of_element_located((by,
                                                                 look_for)))
        except TimeoutException:
            raise TimeoutException(
                'Timed out looking for "{look_for}" by {by}.'.format(
                    look_for=look_for, by=by))
        return result

    def wait(self, tag_name="body", timeout=10):
        # Wait until the response is received
        WebDriverWait(self.selenium, timeout).until(
            lambda driver: driver.find_element_by_tag_name(tag_name))

    def type(self, element, value):
        element.clear()
        element.send_keys(value)

    def login(self, force_new=True):
        if self.logged_in:
            if not force_new:
                return
            else:
                self.logout()

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

        self.logged_in = True

    def logout(self):
        log_out_link = self.patiently_find(look_for='Log Out', by=By.LINK_TEXT)
        log_out_link.click()

    def go_to_reporting_tool(self):
        reporting_tool_tab = self.patiently_find(look_for='Reporting Tool',
                                                 by=By.LINK_TEXT)
        reporting_tool_tab.click()
