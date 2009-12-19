"""
    Test Suite for CMS.  
    These tests cover the CMS, including
     - CMS models
     - xml_rpc backend
     - Article and Category caching
     - template tags
"""
from django.test import TestCase

from stars.apps.cms.models import *
from stars.apps.cms.templatetags import cms_tags

class CMS_tags_Test(TestCase):

    ABOUT_FAQ_ARTICLE_ID = 3743

    def setUp(self):
        articleCategories_sync()
        table, in_sync = articleCategories_perform_consistency_check()
        self.assertTrue(in_sync, "Article Category sync failed - most CMS test will fail as a result")

    """
        #######   cms_tags.py Test Suite.  #######
    """
    def test_show_article_menu_cateogies(self):
        for cat in ArticleCategory.objects.all():            
            context = cms_tags.show_article_menu({'category': cat})
            self.assertEqual(context['article_menu'].__class__, ArticleMenu)
            self.assertEqual(context['mm_category'], cat.get_root_category())
            self.assertEqual(context['sub_category'], cat)
            self.assertEqual(context['current_article'], None)

    def test_show_article_menu_article(self):
        cat, subcat, article  = self._get_test_article_objects()

        context = cms_tags.show_article_menu({'category': subcat, 'article': article})
        self.assertEqual(context['mm_category'], cat)
        self.assertEqual(context['sub_category'], subcat)
        self.assertEqual(context['current_article'], article)

    def test_show_article_menu_no_category(self):
        """ This tests an invalid call - no valid category given - should fail silently and log the error. """
        from stars.apps.tool.admin.watchdog.models import WatchdogEntry
        pre_watchdog_entries = WatchdogEntry.objects.count()
        self.assertEqual( cms_tags.show_article_menu({}), {} )
        self.assertEqual(pre_watchdog_entries+1, WatchdogEntry.objects.count())
        
    def test_show_cms_crumbs(self):
        cat, subcat, article  = self._get_test_article_objects()

        tag_context = cms_tags.show_cms_crumbs(cat)
        self.assertEqual(tag_context['object_set'], [cat])

        tag_context = cms_tags.show_cms_crumbs(subcat)
        self.assertEqual(tag_context['object_set'], [cat, subcat])
    
        tag_context = cms_tags.show_cms_crumbs(article)
        self.assertEqual(tag_context['object_set'], [cat, subcat, article])

    def _get_test_article_objects(self):
        """ 
            Returns a known suite of test article objects:
            category -> subcategory -> article
        """
        cat = ArticleCategory.objects.get(slug='about')
        self.assertEqual(cat.depth, 0)
        self.assertEqual(cat.label, 'About')

        subcat = ArticleCategory.objects.get(slug='faqs')
        self.assertEqual(subcat.depth, 1)
        self.assertEqual(subcat.label, 'FAQs')

        article = Article(node_id=self.ABOUT_FAQ_ARTICLE_ID, category=subcat)

        return cat, subcat, article
    
