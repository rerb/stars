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

from stars.apps.helpers.templatetags import help
class Help_tags_Test(TestCase):

    """
        #######   help.py Test Suite.  #######
    """

    TEST_HELP_TEXT = ("This 'help context' is used by 'automated unit tests' "
                      "- do not change this text!")

    def test_show_help_text_as_tooltip(self):
        context = help.show_help_text(self.TEST_HELP_TEXT)
        self.assertTrue(context['tooltip'])
        self.assertEqual(context['help_text'],
                         self.TEST_HELP_TEXT.replace("'", "\&#39;"))

    def test_show_help_context_as_inline(self):
        context = help.show_help_context("test", False)
        self.assertFalse(context['tooltip'])
        self.assertEqual(context['help_text'], self.TEST_HELP_TEXT)
