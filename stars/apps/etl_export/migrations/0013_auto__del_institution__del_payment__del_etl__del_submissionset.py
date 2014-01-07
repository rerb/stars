# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Institution'
        db.delete_table('etl_export_institution')

        # Deleting model 'Payment'
        db.delete_table('etl_export_payment')

        # Deleting model 'ETL'
        db.delete_table('etl_export_etl')

        # Deleting model 'SubmissionSet'
        db.delete_table('etl_export_submissionset')


    def backwards(self, orm):
        
        # Adding model 'Institution'
        db.create_table('etl_export_institution', (
            ('liaison_department', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('registration_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('submission_due_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('participant_status', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('current_rating', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('last_submission_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('liaison_title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('liaison_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('rating_valid_until', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('liaison_phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('current_stars_version', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('liaison_first_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_last_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('etl_export', ['Institution'])

        # Adding model 'Payment'
        db.create_table('etl_export_payment', (
            ('confirmation', self.gf('django.db.models.fields.CharField')(max_length='16', null=True, blank=True)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length='16')),
            ('user', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('submissionset', self.gf('django.db.models.fields.IntegerField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length='16')),
        ))
        db.send_create_signal('etl_export', ['Payment'])

        # Adding model 'ETL'
        db.create_table('etl_export_etl', (
            ('liaison_department', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('registration_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('submission_due_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('participant_status', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('current_rating', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('last_submission_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'], null=True, blank=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('liaison_title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('liaison_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('rating_valid_until', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('liaison_phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('current_stars_version', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('liaison_first_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_last_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('etl_export', ['ETL'])

        # Adding model 'SubmissionSet'
        db.create_table('etl_export_submissionset', (
            ('status', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('rating', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('date_submitted', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_reviewed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_registered', self.gf('django.db.models.fields.DateField')()),
            ('score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('submission_deadline', self.gf('django.db.models.fields.DateField')()),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('reporter_status', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('etl_export', ['SubmissionSet'])


    models = {
        
    }

    complete_apps = ['etl_export']
