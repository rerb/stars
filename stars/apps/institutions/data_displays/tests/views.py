from mock import patch

from aashe.aasheauth.models import AASHEUser
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

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
    member = UserFactory(password=PASSWORD)
    member.aasheuser = AASHEUser.objects.create(user_id=member.id,
                                                drupal_id=1)
    member.aasheuser.is_member = lambda x: True
    return member


def new_non_member():
    """Return a User that will NOT be identified as a member.
    """
    non_member = UserFactory(password=PASSWORD)
    non_member.aasheuser = AASHEUser.objects.create(user_id=non_member.id,
                                                    drupal_id=2)
    return non_member


GOTTA_BE_A_MEMBER_SENTINEL = 'This Data Display is only accessible to'


class AggregateFilterTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.member = new_member()
        self.non_member = new_non_member()

    def test_categories_data_display_loads(self):
        """Does the Category data display load?
        """
        self.client.login(username=self.non_member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('categories_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)

    def test_categories_data_display_members_only(self):
        """Is the Scores data display held back from non-members?
        """
        self.client.login(username=self.non_member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('categories_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(GOTTA_BE_A_MEMBER_SENTINEL, resp.content)

    def test_categories_data_display_v2_loads(self):
        """Does the Scores data display load for version 2.0 data?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('categories_data_display',
                                       kwargs={'cs_version': '2.0'}))
        self.assertEqual(200, resp.status_code)


class ScoreFilterTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.member = new_member()
        self.non_member = new_non_member()

    def test_scores_data_display_loads(self):
        """Does the Scores data display load?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('scores_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)

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


class ContentFilterTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.member = new_member()
        self.non_member = new_non_member()

    def test_content_data_display_loads(self):
        """Does the Content data display load?
        """
        self.client.login(username=self.non_member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('content_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)

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
