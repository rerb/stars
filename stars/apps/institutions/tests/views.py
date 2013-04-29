"""Tests for apps.institutions.views.
"""
import datetime

from django.test import TestCase
from django.test.client import Client

from aashe.issdjango.models import Organizations

from stars.apps.institutions import views
from stars.apps.institutions.models import Institution
from stars.test_factories import InstitutionFactory,\
    SubscriptionFactory, RatingFactory, CreditSetFactory, \
    SubmissionSetFactory


class ActiveInstitutionsViewTest(TestCase):
    """Test the ActiveInstitutionsView

    This should also test SortableTableView and
    SortableTableViewWithInstProps
    """
    def setUp(self):

        today = datetime.date.today()
        td = datetime.timedelta(days=1)

        # create 3 active Institutions
        for _ in range(3):
            i = InstitutionFactory(is_participant=True)
            s = SubscriptionFactory(start_date=today,
                                    end_date=today+td,
                                    institution=i)
            i.current_subscription = s
            i.save()

        # create 1 non-active Institutions
        for _ in range(1):
            i = InstitutionFactory()
            s = SubscriptionFactory(end_date=today - td, institution=i)
            i.current_subscription = s
            i.save()

    def test_with_client(self):
        """
            This test is enough to cover the code and bring up any
            500 errors. It is not a complete functionality test.
        """

        c = Client()

        # confirm we get a 200 just querying
        url = "/institutions/"
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        view = views.ActiveInstitutions()
        qs = view.get_queryset()
        self.assertEqual(len(qs), 3)

        url = "/institutions/?sort=rating"
        response = c.get(url)
        self.assertEqual(response.status_code, 200)


class RatedInstitutionsViewTest(TestCase):
    """
        Test the RatedInstitutionsView

        This should also test SortableTableView and
        SortableTableViewWithInstProps.
    """
    def setUp(self):

        today = datetime.date.today()
        td = datetime.timedelta(days=1)

        # create 3 rated Institutions
        cs = CreditSetFactory()
        count = 0
        for l in ['a', 'b', 'c', 'd']:
            count += 1
            r = RatingFactory(minimal_score=count, name=l, creditset=cs)
            ss = SubmissionSetFactory(creditset=cs, status='r', rating=r)
            i = InstitutionFactory(is_participant=True,
                                   rated_submission=ss,
                                   current_rating=r)
         # create 1 non-rated Institutions
        for _ in range(1):
            i = InstitutionFactory()
            s = SubscriptionFactory(end_date=today - td)
            i.current_subscription = s
            i.save()

    def test_with_client(self):
        """
            This test is enough to cover the code and bring up any
            500 errors. It is not a complete functionality test.
        """

        c = Client()

        # confirm we get a 200 just querying
        url = "/institutions/rated/"
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        view = views.RatedInstitutions()
        qs = view.get_queryset()
        self.assertEqual(len(qs), 4)

        url = "/institutions/rated/?sort=rating"
        response = c.get(url)
        self.assertEqual(response.status_code, 200)


class ScorecardViewTest(TestCase):
    """
        Test the ScorecardView

        This test is enough to cover the code and bring up any
        500 errors. It is not a complete functionality test.
    """
    fixtures = ['rated_submission.json']

    def setUp(self):
        for i in Institution.objects.all():
            o = Organizations(account_num=i.aashe_id,
                              org_name=i.name,
                              city='city',
                              state='state',
                              exclude_from_website=False)
            o.save()
        self.client = Client()

    def test_with_client(self):
        # confirm we get a 200
        url = "/institutions/rated-college-test/report/2011-01-01/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_submission_date_without_day_returns_404(self):
        """Does a submission date (in the URL) without a day return a 404?"""
        url = "/institutions/rated-college-test/report/2011-01-/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_submission_date_without_month_returns_404(self):
        """Does a submission date (in the URL) without a month return a 404?"""
        url = "/institutions/rated-college-test/report/2011--01/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_submission_date_without_year_returns_404(self):
        """Does a submission date (in the URL) without a year return a 404?"""
        url = "/institutions/rated-college-test/report/-01-01/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_empty_submission_date_returns_404(self):
        """Does an empty submission date (in the URL) return a 404?"""
        url = "/institutions/rated-college-test/report/--/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_submission_date_without_dashes_returns_404(self):
        """Does a submission date (in the URL) without dashes return a 404?"""
        url = "/institutions/rated-college-test/report/20110101/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
