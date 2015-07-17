# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Institution'
        db.create_table('etl_export_institution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('delete_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('liaison_first_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('liaison_last_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('liaison_department', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('liaison_phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('liaison_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('charter_participant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('international', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_participant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('current_rating', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('rating_expires', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('registration_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('current_submission_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('current_subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('rated_submission_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('current_stars_version', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('last_submission_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('submission_due_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('etl_export', ['Institution'])

        # Adding model 'Subscription'
        db.create_table('etl_export_subscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('delete_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('ratings_allocated', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('ratings_used', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('amount_due', self.gf('django.db.models.fields.FloatField')()),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length='16', null=True, blank=True)),
            ('paid_in_full', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('close_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('etl_export', ['Subscription'])

        # Adding model 'SubscriptionPayment'
        db.create_table('etl_export_subscriptionpayment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('delete_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('subscription_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('user', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length='8')),
            ('confirmation', self.gf('django.db.models.fields.CharField')(max_length='16', null=True, blank=True)),
        ))
        db.send_create_signal('etl_export', ['SubscriptionPayment'])

        # Adding model 'SubmissionSet'
        db.create_table('etl_export_submissionset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('delete_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
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

        # Adding model 'Boundary'
        db.create_table('etl_export_boundary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('delete_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('submissionset', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('fte_students', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('undergrad_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('graduate_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('fte_employmees', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('institution_type', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('institutional_control', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('endowment_size', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('student_residential_percent', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('student_ftc_percent', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('student_ptc_percent', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('student_online_percent', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('gsf_building_space', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('gsf_lab_space', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('cultivated_grounds_acres', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('undeveloped_land_acres', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('climate_region', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('ag_school_present', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ag_school_included', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ag_school_details', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('med_school_present', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('med_school_included', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('med_school_details', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pharm_school_present', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pharm_school_included', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pharm_school_details', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pub_health_school_present', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_health_school_included', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_health_school_details', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('vet_school_present', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('vet_school_included', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('vet_school_details', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sat_campus_present', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sat_campus_included', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sat_campus_details', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('hospital_present', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hospital_included', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hospital_details', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('farm_present', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('farm_included', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('farm_acres', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('farm_details', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('agr_exp_present', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('agr_exp_included', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('agr_exp_acres', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('agr_exp_details', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('additional_details', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('etl_export', ['Boundary'])


    def backwards(self, orm):
        # Deleting model 'Institution'
        db.delete_table('etl_export_institution')

        # Deleting model 'Subscription'
        db.delete_table('etl_export_subscription')

        # Deleting model 'SubscriptionPayment'
        db.delete_table('etl_export_subscriptionpayment')

        # Deleting model 'SubmissionSet'
        db.delete_table('etl_export_submissionset')

        # Deleting model 'Boundary'
        db.delete_table('etl_export_boundary')


    models = {
        'etl_export.boundary': {
            'Meta': {'object_name': 'Boundary'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'additional_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ag_school_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ag_school_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ag_school_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'agr_exp_acres': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'agr_exp_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'agr_exp_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'agr_exp_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'climate_region': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'cultivated_grounds_acres': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'delete_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'endowment_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'farm_acres': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'farm_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'farm_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'farm_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fte_employmees': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'fte_students': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'graduate_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'gsf_building_space': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'gsf_lab_space': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'hospital_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hospital_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hospital_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution_type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'institutional_control': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'med_school_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'med_school_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'med_school_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pharm_school_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pharm_school_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pharm_school_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_health_school_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pub_health_school_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_health_school_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sat_campus_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sat_campus_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sat_campus_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_ftc_percent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student_online_percent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student_ptc_percent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student_residential_percent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'submissionset': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'undergrad_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'undeveloped_land_acres': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'vet_school_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'vet_school_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'vet_school_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'etl_export.institution': {
            'Meta': {'object_name': 'Institution'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'charter_participant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'current_rating': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'current_stars_version': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'current_submission_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'current_subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'delete_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'liaison_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rated_submission_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rating_expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'registration_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'submission_due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'etl_export.submissionset': {
            'Meta': {'object_name': 'SubmissionSet'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_registered': ('django.db.models.fields.DateField', [], {}),
            'date_submitted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'delete_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'amount_due': ('django.db.models.fields.FloatField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'close_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'delete_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid_in_full': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'ratings_allocated': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'ratings_used': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'etl_export.subscriptionpayment': {
            'Meta': {'object_name': 'SubscriptionPayment'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'delete_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': "'8'"}),
            'subscription_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        }
    }

    complete_apps = ['etl_export']