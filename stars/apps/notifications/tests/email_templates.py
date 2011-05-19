"""
    Unittests for the EmailTemplate model

    Test premises:
        - utils.build_message()
        - EmailTemplate.get_message()
"""

from django.test import TestCase
from django.core import mail
from django.conf import settings

from stars.apps.notifications.models import EmailTemplate
from stars.apps.notifications.utils import build_message

from datetime import date
import sys, os, random

class TestNotifications(TestCase):

    def setUp(self):
        pass
        
    def test_get_message(self):
        " get_message() "
        
        et = EmailTemplate(
                            slug='test_slug',
                            title='Test Title',
                            description='Testing this thing',
                            content="This is the <b>value</b> '{{ test_val }}'.",
                            example_context="{'test_val': 1,}"
                            )
        et.save()
        
        self.assertEqual(et.get_message(), "This is the <b>value</b> '1'.")