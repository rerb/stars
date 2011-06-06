"""
    Submission Migration unit tests
    
    Test Premises:
     - Migrate from 1.0 to 1.1 w/out data
     - Migrate from 1.0 to 1.1 w/ data
     - Don't migrate 1.1 to 1.1
     
"""
from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.conf import settings

from stars.apps.submissions.utils import migrate_submission
from stars.apps.submissions.models import *

import sys

class MigrationTest(TestCase):
    fixtures = ['submission_migration_test.json','notification_emailtemplate_tests.json']

    def setUp(self):
        
        settings.CELERY_ALWAYS_EAGER = True

    def testMigration(self):
        """
            migrate_submission()
        """
        
        # Authenticate the user
        c = Client()
        c.login(username='tester', password='test')
        
        # Just check the migration page returns a 200 response
        response = c.get('/tool/manage/submissionsets/1/migrate/')
        self.assertTrue(response.status_code == 200)
        
        # Now submit for a migration
        post_dict = {
            "1-is_locked": "on"
        }
        response = c.post('/tool/manage/submissionsets/1/migrate/', post_dict)
        self.assertTrue(response.status_code == 302)
        
        # Check that the data was migrated correctly
        ## SubmissionSet added
        self.assertEqual(SubmissionSet.objects.count(), 2)
        
        ## Documentation field data migrated
        self.assertEqual(NumericSubmission.objects.count(), 2)
        ns1 = NumericSubmission.objects.all()[0]
        ns2 = NumericSubmission.objects.all()[1]
        self.assertEqual(ns1.value, ns2.value)
        
        # Check that an email was sent.
        self.assertEqual(len(mail.outbox), 1)