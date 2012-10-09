"""Tests for apps.submissions.pdf.export.
"""
from unittest import TestCase

import testfixtures

from stars.apps.submissions.pdf import export


class PDFExportTest(TestCase):

    def test_render_to_pdf_logging(self):
        """Does render_to_pdf log an error when there's one occurs?
        """

        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.submissions.pdf.export.get_template',
                          lambda x: MockTemplate(x))
                r.replace('stars.apps.submissions.pdf.export.Context',
                          MockContext)
                r.replace('stars.apps.submissions.pdf.export.pisa',
                          MockPisa())
                export.render_to_pdf(template_src='<html>no bob</html>',
                                     context_dict={'bob': 'erb'})

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'PDF Generation Failed'))


class MockPisa(object):

    def pisaDocument(self, html, result):
        return MockPDF()


class MockPDF(object):

    def __init__(self):
        self.err = 'Oh no!'


class MockTemplate(object):

    def __init__(self, template_src):
        self.template_src = template_src

    def render(self, context):
        return self.template_src


class MockContext(object):

    def __init__(self, context_dict):
        self.context_dict = context_dict
