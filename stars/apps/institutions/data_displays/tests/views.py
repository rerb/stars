# -*- coding: utf-8 -*-
import datetime

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from selenium.webdriver.support.ui import Select

from stars.apps.credits.models import CreditSet
# from stars.apps.tests.live_server import StarsLiveServerTest
from stars.test_factories import SubscriptionFactory, UserFactory


class DashboardTestCase(TestCase):

    def setUp(self):
        # Need at least some history.
        _ = SubscriptionFactory()

    def test_dashboard_loads(self):
        """Does the dashboard load?
        """
        client = Client()
        resp = client.get(reverse('dashboard'))
        self.assertEqual(200, resp.status_code)


PASSWORD = 'password'


def new_member():
    """Return a User that will be identified as a member.
    """
    user = UserFactory(password=PASSWORD)
    user.aasheuser.set_drupal_user_dict(
        {'roles': {'Member': 'Member'}})
    user.aasheuser.save()
    return user


def new_non_member():
    """Return a User that will NOT be identified as a member.
    """
    non_member = UserFactory(password=PASSWORD)
    return non_member


GOTTA_BE_A_MEMBER_SENTINEL = 'This Data Display is only accessible to'
FILTERS_SHOW_SENTINEL = 'Select a filter'


def create_creditset(version):
    if version.startswith('1'):
        scoring_method = 'STARS 1.0 Scoring'
    else:
        scoring_method = 'STARS 2.0 Scoring'
    creditset = CreditSet.objects.create(
        version=version,
        release_date=datetime.date.today(),
        tier_2_points=0,
        scoring_method=scoring_method)
    return creditset


def create_creditsets():
    _ = create_creditset('1.0')
    _ = create_creditset('1.2')
    _ = create_creditset('2.0')


class AggregateFilterTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.member = new_member()
        self.non_member = new_non_member()
        create_creditsets()

    def test_categories_data_display_loads(self):
        """Does the Category data display load?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('categories_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)

    def test_categories_data_display_members_only(self):
        """Is the Category data display held back from non-members?
        """
        self.client.login(username=self.non_member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('categories_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(GOTTA_BE_A_MEMBER_SENTINEL, resp.content)

    def test_categories_data_display_v2_loads(self):
        """Does the Category data display load for version 2.0 data?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('categories_data_display',
                                       kwargs={'cs_version': '2.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)


class ScoreFilterTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.member = new_member()
        self.non_member = new_non_member()
        create_creditsets()

    def test_scores_data_display_loads(self):
        """Does the Scores data display load?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('scores_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)

    def test_scores_data_display_members_only(self):
        """Is the Scores data display held back from non-members?
        """
        self.client.login(username=self.non_member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('scores_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(GOTTA_BE_A_MEMBER_SENTINEL, resp.content)

    def test_scores_data_display_v2_loads(self):
        """Does the Scores data display load for version 2.0 data?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('scores_data_display',
                                       kwargs={'cs_version': '2.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)


class ContentFilterTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.member = new_member()
        self.non_member = new_non_member()
        create_creditsets()

    def test_content_data_display_loads(self):
        """Does the Content data display load?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('content_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)

    def test_content_data_display_members_only(self):
        """Is the Content data display held back from non-members?
        """
        self.client.login(username=self.non_member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('content_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(GOTTA_BE_A_MEMBER_SENTINEL, resp.content)

    def test_content_data_display_v2_loads(self):
        """Does the Content data display load for version 2.0 data?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('content_data_display',
                                       kwargs={'cs_version': '2.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)


# class DataDisplayLiveServerTest(StarsLiveServerTest):

#     def setUp(self):
#         super(DataDisplayLiveServerTest, self).setUp()
#         self.selenium.implicitly_wait(30)

#     def test_can_add_category_filter(self):
#         """Can we add a filter on the Category data display?
#         """
#         self.user = new_member()
#         import ipdb; ipdb.set_trace()
#         self.selenium.get(self.live_server_url)
#         self.selenium.find_element_by_link_text(
#             u"Explore the Data »").click()
#         self.selenium.find_element_by_link_text("Category Display").click()
#         Select(self.selenium.find_element_by_id(
#             "filter_type")).select_by_visible_text("Country")
#         Select(self.selenium.find_element_by_id(
#             "filter_options")).select_by_visible_text("Canada")
#         self.selenium.find_element_by_xpath(
#             "//button[@type='button']").click()
