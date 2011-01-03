"""
    Test Suite for Helpers.  
    These tests cover all of the helpers, including
     - form helpers
     - exceptions
     - widgets
     - xmlrpc client
     - template tags
"""
from django.test import TestCase

from stars.apps.helpers.templatetags import help, main_menu
class Help_tags_Test(TestCase):

    """
        #######   main_menu.py Test Suite.  #######
    """
    def test_show_main_menu_as_anonymous(self):
        context = main_menu.show_main_menu(False, None)
        menu_items = context['menu_items']
        self.assertEqual(len(menu_items), 2)
        self.assertEqual(menu_items[0].label, "Reporting Tool")
        self.assertEqual(menu_items[0].href, "/tool/")
        self.assertEqual(menu_items[0].css_class, "")

    def test_show_main_menu_as_authenticated(self):
        context = main_menu.show_main_menu(True, None)
        menu_items = context['menu_items']
        self.assertEqual(len(menu_items), 2)
        self.assertEqual(menu_items[1].label, "STARS Institutions")
        self.assertEqual(menu_items[1].href, "/institutions/")
        self.assertEqual(menu_items[1].css_class, "")

    def test_show_main_menu_with_current(self):
        context = main_menu.show_main_menu(True, "institutions")
        self.assertEqual(context['menu_items'][0].css_class, "")
        self.assertEqual(context['menu_items'][1].css_class, "current")
        context = main_menu.show_main_menu(True, "tool")
        self.assertEqual(context['menu_items'][0].css_class, "current")
        self.assertEqual(context['menu_items'][1].css_class, "")

    def test_show_main_menu_with_articles(self):
        # Note: this test may fail if categories on IRC are modified, which seems likely!
        from stars.apps.cms.models import articleCategories_sync, articleCategories_perform_consistency_check
        articleCategories_sync()
        table, in_sync = articleCategories_perform_consistency_check()
        self.assertTrue(in_sync, "Article Category sync failed - main menu test will fail as a result")
        context = main_menu.show_main_menu(True, "")
        menu_items = context['menu_items']
        self.assertEqual(len(menu_items), 5)
        self.assertEqual(menu_items[0].label, "Reporting Tool")
        self.assertEqual(menu_items[1].label, "News & Events")
        # other categories were loaded - but order or names may change, so leave them be...
        self.assertEqual(menu_items[-1].label, "About")
        
    """
        #######   help.py Test Suite.  #######
    """
    def test_show_help_context_as_tooltip(self):
        context = help.show_help_context("test")
        # test help text is:  This 'help context' is used by "automated unit tests" - do not change this text!
        self.assertTrue(context['tooltip'])
        self.assertEqual(context['help_text'], "This \&#39;help context\&#39; is used by \&quot;automated unit tests\&quot; - do not change this text!")

    def test_show_help_context_as_inline(self):
        context = help.show_help_context("test", False)
        # test help text is:  This 'help context' is used by "automated unit tests" - do not change this text!
        self.assertFalse(context['tooltip'])
        self.assertEqual(context['help_text'], "This \'help context\' is used by \"automated unit tests\" - do not change this text!")

    def test_show_help_text_as_tooltip(self):
        context = help.show_help_text("This 'help context' is used by \"automated unit tests\" - do not change this text!")
        # test help text is:  This 'help context' is used by "automated unit tests" - do not change this text!
        self.assertTrue(context['tooltip'])
        self.assertEqual(context['help_text'], "This \\&#39;help context\\&#39; is used by \\&quot;automated unit tests\\&quot; - do not change this text!")

    def test_show_help_text_as_inline(self):
        context = help.show_help_text("This 'help context' is used by \"automated unit tests\" - do not change this text!", False)
        # test help text is:  This 'help context' is used by "automated unit tests" - do not change this text!
        self.assertFalse(context['tooltip'])
        self.assertEqual(context['help_text'], "This \'help context\' is used by \"automated unit tests\" - do not change this text!")
