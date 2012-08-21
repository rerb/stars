"""Tests for stars.apps.cms.templatetags.cms_tags.
"""
from unittest import TestCase

import testfixtures


class CMSTagsTest(TestCase):

    def test_show_article_menu_logging(self):
        """Does show_article_menu log an exception if one occurs?
        """
        # Moved this import into this TestCase because it fails.
        # Leaving in the top level of this module causes a test run to
        # halt; putting here causes the test to fail, which it should.
        from stars.apps.cms.templatetags import cms_tags

        with testfixtures.LogCapture('stars') as log:
            dummy_context = {}
            cms_tags.show_article_menu(dummy_context)

        self.assertEqual(len(log.records), 1)
        for record in log.records:
            self.assertEqual(record.levelname, 'ERROR')
