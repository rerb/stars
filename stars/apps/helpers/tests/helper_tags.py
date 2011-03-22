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
