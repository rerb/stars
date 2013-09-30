"""
    Submission Migration unit tests

    Test Premises:
     - Migrate from 1.0 to 1.1 w/out data
     - Migrate from 1.0 to 1.1 w/ data
     - Don't migrate 1.1 to 1.1

"""
from datetime import datetime, timedelta

from django.core import mail
from django.test import TestCase

from stars.apps.migrations import utils
from stars.apps.submissions.models import SubmissionSet
from stars.apps.tests.live_server import StarsLiveServerTest
from stars.test_factories import (CreditSetFactory,
                                  EmailTemplateFactory,
                                  SubmissionSetFactory)


def go_to_migration_options_page(test, webdriver):
    test.go_to_reporting_tool()
    migrate_tab = webdriver.find_element_by_link_text('Migrate')
    migrate_tab.click()


def make_two_creditsets():
    return (CreditSetFactory(release_date='1970-01-01'),
            CreditSetFactory(release_date='1971-10-07'))


class VersionMigrationTest(TestCase):

    def setUp(self):
        super(VersionMigrationTest, self).setUp()
        self.first_creditset, self.second_creditset = make_two_creditsets()
        self._submissionset = None

    @property
    def submissionset(self):
        if not self._submissionset:
            self._submissionset = SubmissionSetFactory(
                creditset=self.first_creditset)
        return self._submissionset

    def test_migrate_submission_sets_migrated_from(self):
        """Does migrate_submission() set SubmissionSet.migrated_from?"""

        new_submissionset = SubmissionSetFactory(
            institution=self.submissionset.institution,
            creditset=self.second_creditset)

        _ = utils.migrate_submission(old_ss=self.submissionset,
                                     new_ss=new_submissionset)

        self.assertEqual(new_submissionset.migrated_from,
                         self.submissionset)


class VersionMigrationLiveServerTest(StarsLiveServerTest):

    def setUp(self):
        super(VersionMigrationLiveServerTest, self).setUp()
        first_creditset, _ = make_two_creditsets()
        _ = SubmissionSetFactory(institution=self.institution,
                                 creditset=first_creditset)
        _ = EmailTemplateFactory(slug='migration_success')
        go_to_migration_options_page(self, self.selenium)

    def test_version_migration(self):
        """Does migrating to new version make new SubmissionSet and send mail?
        """
        num_submission_sets_before = SubmissionSet.objects.count()

        migrate_now_button = self.selenium.find_element_by_link_text(
            'Migrate Now')
        migrate_now_button.click()

        are_you_sure_checkbox = self.selenium.find_element_by_id(
            'id_is_locked')
        are_you_sure_checkbox.click()

        migrate_version_button = self.selenium.find_element_by_css_selector(
            'button.btn.btn-success')
        migrate_version_button.click()

        # SubmissionSet added?
        self.assertEqual(SubmissionSet.objects.count(),
                         num_submission_sets_before + 1)

        # Check that an email was sent.
        mail_messages_that_are_not_errors = [ msg for msg in mail.outbox if
                                              'ERROR:' not in msg.subject ]
        self.assertEqual(len(mail_messages_that_are_not_errors), 1)


class DataMigrationLiveServerTest(StarsLiveServerTest):

    def setUp(self):
        super(DataMigrationLiveServerTest, self).setUp()
        creditset = CreditSetFactory()
        _ = SubmissionSetFactory(creditset=creditset,
                                 institution=self.institution,
                                 date_registered=datetime.now(),
                                 registering_user=self.user,
                                 status='r',
                                 is_locked=False,
                                 is_visible=True)
        _ = EmailTemplateFactory(slug='migration_success')
        go_to_migration_options_page(self, self.selenium)

    def test_data_migration(self):
        """Does migrating data make a new SubmissionSet and show success msg?
        """
        num_submission_sets_before = SubmissionSet.objects.count()

        migrate_button = self.selenium.find_element_by_css_selector(
            'a.btn.btn-mini')
        migrate_button.click()

        confirmation_checkbox = self.patiently_find('id_is_locked')
        confirmation_checkbox.click()

        migrate_my_data_button = self.patiently_find('migrate-my-data-button')
        migrate_my_data_button.click()

        migration_in_progress_message = 'migration is in progress'
        for alert in self.selenium.find_elements_by_class_name('alert'):
            if migration_in_progress_message in alert.text:
                break
        else:
            self.assertTrue(False, 'No alert with {msg} found'.format(
                msg=migration_in_progress_message))

        self.assertEqual(SubmissionSet.objects.count(),
                         num_submission_sets_before + 1)
