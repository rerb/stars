from django.contrib.auth.models import User
from django.test import TestCase

from stars.apps.institutions.data_displays.filters import Filter


class FilterTestCase(TestCase):

    def setUp(self):
        self.filter = Filter(key='is_active',
                             title='Is Active',
                             item_list=(('Yes', 'True'),
                                        ('No', 'False')),
                             base_qs=User.objects.all())

    def make_some_users(self):
        User.objects.create(email='one@example.com',
                            username='one')
        User.objects.create(email='two@example.com',
                            username='two')
        User.objects.create(email='three@example.com',
                            username='three')

    def test_get_active_title_when_key_rating_name(self):
        """Does get_active_title work when key == 'rating_name'?
        """
        filter = Filter(key='rating__name',
                        title='Rating Name',
                        item_list=None,
                        base_qs=None)
        self.assertEqual('True Rated Institutions',
                         filter.get_active_title(item='True'))

    def test_get_active_title_when_key_not_rating_name(self):
        """Does get_active_title work when key != 'rating_name'?
        """
        self.assertEqual(True,
                         self.filter.get_active_title(item='True'))

    def test_get_select_list(self):
        self.assertEqual(
            self.filter.item_list,
            filter.get_select_list())

    def test_get_results_DO_NOT_FILTER(self):
        """Does get_results handle the DO_NOT_FILTER flag?
        """
        self.make_some_users()
        self.assertEqual(
            3,
            self.filter.get_results(item='DO_NOT_FILTER').count())

    def test_get_results_filter(self):
        """Does get_results handle a filter?
        """
        self.make_some_users()
        one = User.objects.get(pk=1)
        one.is_active = True
        one.save()
        two = User.objects.get(pk=2)
        two.is_active = False
        two.save()
        three = User.objects.get(pk=3)
        three.is_active = False
        three.save()

        self.assertEqual(2,
                         self.filter.get_results(item='False').count())
