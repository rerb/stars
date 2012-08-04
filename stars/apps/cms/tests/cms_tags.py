"""Tests for stars.apps.cms.templatetags.cms_tags.
"""
from unittest import TestCase

import testfixtures

from stars.apps.cms.templatetags import cms_tags


class CMSTagsTest(TestCase):

    def test_show_article_menu_logging(self):
        """Does show_article_menu log an exception if one occurs?"""
        with testfixtures.LogCapture('stars') as log:
            dummy_context = {}
            cms_tags.show_article_menu(dummy_context)

        self.assertEqual(len(log.records), 1)
        for record in log.records:
            self.assertEqual(record.levelname, 'ERROR')
            self.assertTrue(record.module_path.startswith('stars'))
