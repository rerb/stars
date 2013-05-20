"""
    Tests for apps/cms/views.py.
"""
from django.test import TestCase
from django.test.client import RequestFactory

from stars.apps.cms.models import Category, NewArticle, Subcategory
from stars.apps.cms.views import ArticleDetailView, CategoryDetailView, \
     CMSView, OldPathRedirectView, SubcategoryDetailView

request_factory = RequestFactory()
test_category = test_subcategory = test_article = None

def setUpModule():
    global test_category, test_subcategory, test_article
    test_category = Category(slug='nancy', published=True)
    test_category.save()
    test_subcategory = Subcategory(slug='nickel', published=True,
                                   parent=test_category)
    test_subcategory.save()
    test_article = NewArticle(slug='bug', published=True)
    test_article.save()
    test_article.categories = [test_category]
    test_article.subcategories = [test_subcategory]
    test_article.save()

def tearDownModule():
    test_article.delete()
    test_subcategory.delete()
    test_category.delete()


class CMSViewTest(TestCase):

    def test_get_context_data_finds_category_by_slug(self):
        """Does get_context_data get the category for category_slug kwarg?"""
        context_data = CMSView().get_context_data(
            category_slug=test_category.slug)
        self.assertEqual(context_data['category'], test_category)

    def test_get_context_data_finds_subcategory_by_slug(self):
        """Does get_context_data find the subcategory for subcategory_slug kw?"""
        context_data = CMSView().get_context_data(
            category_slug=test_category.slug,
            subcategory_slug=test_subcategory.slug)
        self.assertEqual(context_data['subcategory'], test_subcategory)

    def test_get_context_data_finds_article_by_slug(self):
        """Does get_context_data find the artile for article_slug kwarg?"""
        context_data = CMSView().get_context_data(
            category_slug=test_category.slug,
            subcategory_slug=test_subcategory.slug,
            article_slug=test_article.slug)
        self.assertEqual(context_data['article'], test_article)


class ArticleDetailViewTest(TestCase):

    def test_successful_response(self):
        """Does ArticleDetailView.as_view() return a successful response?"""
        response = ArticleDetailView.as_view()(
            request_factory.get('/'),
            category_slug=test_category.slug,
            subcategory_slug=test_subcategory.slug,
            article_slug=test_article.slug)
        self.assertEqual(response.status_code, 200)


class CategoryDetailViewTest(TestCase):

    def test_successful_response(self):
        """Does CategoryDetailView.as_view() return a successful response?"""
        response = CategoryDetailView.as_view()(
            request_factory.get('/'),
            category_slug=test_category.slug)
        self.assertEqual(response.status_code, 200)


class SubcategoryDetailViewTest(TestCase):

    def test_successful_response(self):
        """Does SubcategoryDetailView.as_view() return a successful response?"""
        response = SubcategoryDetailView.as_view()(
            request_factory.get('/'),
            category_slug=test_category.slug,
            subcategory_slug=test_subcategory.slug)
        self.assertEqual(response.status_code, 200)


class OldPathRedirectViewTest(TestCase):

    def test_redirect_to_successful_response(self):
        """Does OldPathRedirectView.as_view() send to a successful response?"""
        IRC_ID = 500000
        test_article.irc_id = IRC_ID
        test_article.save()

        # Get a redirect:
        response = OldPathRedirectView.as_view()(request_factory.get('/'),
                                                 nid=IRC_ID)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['location'], test_article.get_absolute_url())

        # View the redirect through the ArticleDetailView:
        request = request_factory.get(response['location'])
        response = ArticleDetailView.as_view()(request)
        self.assertEqual(response.status_code, 200)
