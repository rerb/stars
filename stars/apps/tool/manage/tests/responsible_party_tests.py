"""
    Unittests for the submission renewal process
"""
from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.contrib.auth.models import User

from datetime import date
import sys, os, random

from stars.apps.submissions.models import ResponsibleParty

class ResponisblePartyTest(TestCase):
    fixtures = ['responsible_party_test_data.json']

    def setUp(self):
        pass
    
    def test_delete(self):
        """
        
        """
        print self.fixtures
        user = User.objects.get(pk=1)
        user.set_password('test')
        user.save()
        
        c = Client()
        login = c.login(username='tester', password='test')
        self.assertTrue(login)
        
        rp_url = "/tool/manage/responsible-parties/1/"
        rp_del_url = "/tool/manage/responsible-parties/1/delete/"
        
        # RP Page Loads... and RP exists
        response = c.get(rp_url)
        self.assertTrue(response.status_code == 200)

        # Delete should fail and redirect to RP 
        response = c.get(rp_del_url)
        self.assertTrue(response.status_code == 302)
        self.assertEqual(response['Location'], "http://testserver/tool/manage/responsible-parties/1/")

        # Confirm RP1 still exists
        self.assertEqual(ResponsibleParty.objects.count(), 2)
        
        rp_url = "/tool/manage/responsible-parties/2/"
        rp_del_url = "/tool/manage/responsible-parties/2/delete/"

        # RP Page Loads... and RP exists
        response = c.get(rp_url)
        self.assertTrue(response.status_code == 200)

        # Delete should succeed and redirect to RP list 
        response = c.get(rp_del_url)
        self.assertTrue(response.status_code == 302)
        self.assertEqual(response['Location'], "http://testserver/tool/manage/responsible-parties/")

        # Confirm RP2 still exists
        self.assertEqual(ResponsibleParty.objects.count(), 1)
