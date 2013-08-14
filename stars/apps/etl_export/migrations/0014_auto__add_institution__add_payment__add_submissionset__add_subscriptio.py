# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Institution'
        db.create_table('etl_export_institution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('liaison_first_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('liaison_last_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('liaison_department', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('liaison_phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('liaison_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('charter_participant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('international', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_participant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('current_rating', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('rating_expires', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('current_submission', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current', null=True, to=orm['etl_export.SubmissionSet'])),
            ('current_subscription', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current', null=True, to=orm['etl_export.Subscription'])),
            ('rated_submission', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='rated', null=True, to=orm['etl_export.SubmissionSet'])),
            ('current_stars_version', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('rating_valid_until', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('registration_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('last_submission_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('submission_due_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('etl_export', ['Institution'])

        # Adding model 'Payment'
        db.create_table('etl_export_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('subscription', self.gf('django.db.models.fields.IntegerField')()),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('user', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length='16')),
            ('method', self.gf('django.db.models.fields.CharField')(max_length='16')),
            ('confirmation', self.gf('django.db.models.fields.CharField')(max_length='16', null=True, blank=True)),
        ))
        db.send_create_signal('etl_export', ['Payment'])

        # Adding model 'SubmissionSet'
        db.create_table('etl_export_submissionset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('date_registered', self.gf('django.db.models.fields.DateField')()),
            ('date_submitted', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('registering_user', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('submitting_user', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('rating', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('reporter_status', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('etl_export', ['SubmissionSet'])

        # Adding model 'Subscription'
        db.create_table('etl_export_subscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('ratings_allocated', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('ratings_used', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('paid_in_full', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('etl_export', ['Subscription'])

        # Adding model 'SubscriptionPayment'
        db.create_table('etl_export_subscriptionpayment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['etl_export.Subscription'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('user', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length='16')),
            ('method', self.gf('django.db.models.fields.CharField')(max_length='8')),
            ('confirmation', self.gf('django.db.models.fields.CharField')(max_length='16', null=True, blank=True)),
        ))
        db.send_create_signal('etl_export', ['SubscriptionPayment'])


    def backwards(self, orm):
        
        # Deleting model 'Institution'
        db.delete_table('etl_export_institution')

        # Deleting model 'Payment'
        db.delete_table('etl_export_payment')

        # Deleting model 'SubmissionSet'
        db.delete_table('etl_export_submissionset')

        # Deleting model 'Subscription'
        db.delete_table('etl_export_subscription')

        # Deleting model 'SubscriptionPayment'
        db.delete_table('etl_export_subscriptionpayment')


    models = {
        'etl_export.institution': {
            'Meta': {'object_name': 'Institution'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'charter_participant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'current_rating': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'current_stars_version': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'current_submission': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current'", 'null': 'True', 'to': "orm['etl_export.SubmissionSet']"}),
            'current_subscription': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current'", 'null': 'True', 'to': "orm['etl_export.Subscription']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'international': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_participant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_submission_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'liaison_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'liaison_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'liaison_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'liaison_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'liaison_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'liaison_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'liaison_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'rated_submission': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rated'", 'null': 'True', 'to': "orm['etl_export.SubmissionSet']"}),
            'rating_expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'rating_valid_until': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'registration_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'submission_due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'etl_export.payment': {
            'Meta': {'object_name': 'Payment'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': "'16'"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'16'"}),
            'subscription': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        },
        'etl_export.submissionset': {
            'Meta': {'object_name': 'SubmissionSet'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_registered': ('django.db.models.fields.DateField', [], {}),
            'date_submitted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rating': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'registering_user': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'reporter_status': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'submitting_user': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'etl_export.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid_in_full': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'ratings_allocated': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'ratings_used': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'etl_export.subscriptionpayment': {
            'Meta': {'object_name': 'SubscriptionPayment'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': "'8'"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'16'"}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['etl_export.Subscription']"}),
            'user': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        }
    }

    complete_apps = ['etl_export']
