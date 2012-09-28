"""Tests for apps.helpers.shortcuts.
"""
from unittest import TestCase

import testfixtures
from django.http import Http404

from stars.apps.helpers import shortcuts


class ShortcutsTest(TestCase):

    def test_get_cmsobject_or_404_logging(self):
        """
        Does get_cmsobject_or_404 log a message and exception if no resource?
        """
        with testfixtures.LogCapture('stars') as log:
            self.assertRaises(Http404,
                              shortcuts.get_cmsobject_or_404,
                              lambda x: None, 'arg_for_lambda')

        self.assertEqual(len(log.records), 2)

        self.assertEqual(log.records[0].levelname, 'INFO')
        self.assertTrue('failed' in log.records[0].msg)

        self.assertEqual(log.records[1].levelname, 'ERROR')
        self.assertTrue('resource was not found' in log.records[1].msg.message)
        self.assertTrue(log.records[1].exc_info)
