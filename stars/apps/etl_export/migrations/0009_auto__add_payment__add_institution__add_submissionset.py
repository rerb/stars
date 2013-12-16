# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Payment'
        db.create_table('etl_export_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('submissionset', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('user', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length='8')),
            ('type', self.gf('django.db.models.fields.CharField')(max_length='8')),
            ('confirmation', self.gf('django.db.models.fields.CharField')(max_length='16', null=True, blank=True)),
        ))
        db.send_create_signal('etl_export', ['Payment'])

        # Adding model 'Institution'
        db.create_table('etl_export_institution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('participant_status', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('current_rating', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('rating_valid_until', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('registration_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('last_submission_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('submission_due_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('current_stars_version', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('liaison_first_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('liaison_last_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('liaison_department', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('liaison_phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('liaison_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('etl_export', ['Institution'])

        # Adding model 'SubmissionSet'
        db.create_table('etl_export_submissionset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('date_registered', self.gf('django.db.models.fields.DateField')()),
            ('date_submitted', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_reviewed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('submission_deadline', self.gf('django.db.models.fields.DateField')()),
            ('rating', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('reporter_status', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('etl_export', ['SubmissionSet'])


    def backwards(self, orm):
        
        # Deleting model 'Payment'
        db.delete_table('etl_export_payment')

        # Deleting model 'Institution'
        db.delete_table('etl_export_institution')

        # Deleting model 'SubmissionSet'
        db.delete_table('etl_export_submissionset')


    models = {
        'etl_export.etl': {
            'Meta': {'object_name': 'ETL'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'current_rating': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'current_stars_version': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']", 'null': 'True', 'blank': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_submission_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'liaison_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'liaison_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'liaison_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'liaison_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'liaison_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'liaison_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'liaison_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'participant_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'rating_valid_until': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'registration_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'submission_due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'etl_export.institution': {
            'Meta': {'object_name': 'Institution'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'current_rating': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'current_stars_version': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_submission_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'liaison_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'liaison_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'liaison_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'liaison_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'liaison_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'liaison_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'liaison_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'participant_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'rating_valid_until': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'registration_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'submission_due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'etl_export.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'8'"}),
            'submissionset': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': "'8'"}),
            'user': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        },
        'etl_export.submissionset': {
            'Meta': {'object_name': 'SubmissionSet'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_registered': ('django.db.models.fields.DateField', [], {}),
            'date_reviewed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_submitted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'reporter_status': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'submission_deadline': ('django.db.models.fields.DateField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'institutions.institution': {
            'Meta': {'object_name': 'Institution'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'charter_participant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'contact_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'contact_phone_ext': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'contact_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'executive_contact_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'executive_contact_city': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'executive_contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'executive_contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'executive_contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'executive_contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'executive_contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'executive_contact_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'executive_contact_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'executive_contact_zip': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'stars_staff_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['etl_export']
