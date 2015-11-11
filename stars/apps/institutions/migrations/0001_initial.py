# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClimateZone'
        db.create_table('institutions_climatezone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('institutions', ['ClimateZone'])

        # Adding model 'Institution'
        db.create_table('institutions_institution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('contact_first_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('contact_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('contact_last_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('contact_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('contact_department', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('contact_phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('contact_phone_ext', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('contact_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('executive_contact_first_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('executive_contact_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('executive_contact_last_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('executive_contact_title', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('executive_contact_department', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('executive_contact_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('executive_contact_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('executive_contact_city', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('executive_contact_state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('executive_contact_zip', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('president_first_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('president_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('president_last_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('president_title', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('president_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('president_city', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('president_state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('president_zip', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('charter_participant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('stars_staff_notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('international', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, blank=True)),
            ('org_type', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('fte', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_pcc_signatory', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('is_member', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('is_pilot_participant', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('is_participant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('current_rating', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Rating'], null=True, blank=True)),
            ('rating_expires', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('current_submission', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current', null=True, to=orm['submissions.SubmissionSet'])),
            ('current_subscription', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current', null=True, to=orm['institutions.Subscription'])),
            ('rated_submission', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='rated', null=True, to=orm['submissions.SubmissionSet'])),
            ('latest_expired_submission', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='latest_expired', null=True, to=orm['submissions.SubmissionSet'])),
            ('prefers_metric_system', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('institutions', ['Institution'])

        # Adding model 'MigrationHistory'
        db.create_table('institutions_migrationhistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('source_ss', self.gf('django.db.models.fields.related.ForeignKey')(related_name='migration_sources', to=orm['submissions.SubmissionSet'])),
            ('target_ss', self.gf('django.db.models.fields.related.ForeignKey')(related_name='migration_targets', to=orm['submissions.SubmissionSet'])),
        ))
        db.send_create_signal('institutions', ['MigrationHistory'])

        # Adding model 'Subscription'
        db.create_table('institutions_subscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('ratings_allocated', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('ratings_used', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('amount_due', self.gf('django.db.models.fields.FloatField')()),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length='16', null=True, blank=True)),
            ('paid_in_full', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('late', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('institutions', ['Subscription'])

        # Adding model 'SubscriptionPayment'
        db.create_table('institutions_subscriptionpayment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Subscription'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('method', self.gf('django.db.models.fields.CharField')(max_length='8')),
            ('confirmation', self.gf('django.db.models.fields.CharField')(max_length='16', null=True, blank=True)),
        ))
        db.send_create_signal('institutions', ['SubscriptionPayment'])

        # Adding model 'RegistrationReason'
        db.create_table('institutions_registrationreason', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('institutions', ['RegistrationReason'])

        # Adding model 'RegistrationSurvey'
        db.create_table('institutions_registrationsurvey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('source', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('other', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('primary_reason', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='primary_surveys', null=True, to=orm['institutions.RegistrationReason'])),
            ('enhancements', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('institutions', ['RegistrationSurvey'])

        # Adding M2M table for field reasons on 'RegistrationSurvey'
        m2m_table_name = db.shorten_name('institutions_registrationsurvey_reasons')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('registrationsurvey', models.ForeignKey(orm['institutions.registrationsurvey'], null=False)),
            ('registrationreason', models.ForeignKey(orm['institutions.registrationreason'], null=False))
        ))
        db.create_unique(m2m_table_name, ['registrationsurvey_id', 'registrationreason_id'])

        # Adding model 'RespondentRegistrationReason'
        db.create_table('institutions_respondentregistrationreason', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('institutions', ['RespondentRegistrationReason'])

        # Adding model 'RespondentSurvey'
        db.create_table('institutions_respondentsurvey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('source', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('other', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('potential_stars', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
        ))
        db.send_create_signal('institutions', ['RespondentSurvey'])

        # Adding M2M table for field reasons on 'RespondentSurvey'
        m2m_table_name = db.shorten_name('institutions_respondentsurvey_reasons')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('respondentsurvey', models.ForeignKey(orm['institutions.respondentsurvey'], null=False)),
            ('respondentregistrationreason', models.ForeignKey(orm['institutions.respondentregistrationreason'], null=False))
        ))
        db.create_unique(m2m_table_name, ['respondentsurvey_id', 'respondentregistrationreason_id'])

        # Adding model 'InstitutionPreferences'
        db.create_table('institutions_institutionpreferences', (
            ('institution', self.gf('django.db.models.fields.related.OneToOneField')(related_name='preferences', unique=True, primary_key=True, to=orm['institutions.Institution'])),
            ('notify_users', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('institutions', ['InstitutionPreferences'])

        # Adding model 'BaseAccount'
        db.create_table('institutions_baseaccount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('institutions', ['BaseAccount'])

        # Adding model 'StarsAccount'
        db.create_table('institutions_starsaccount', (
            ('baseaccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['institutions.BaseAccount'], unique=True, primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
            ('terms_of_service', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user_level', self.gf('django.db.models.fields.CharField')(max_length='6')),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_selected', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('institutions', ['StarsAccount'])

        # Adding unique constraint on 'StarsAccount', fields ['user', 'institution']
        db.create_unique('institutions_starsaccount', ['user_id', 'institution_id'])

        # Adding model 'PendingAccount'
        db.create_table('institutions_pendingaccount', (
            ('baseaccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['institutions.BaseAccount'], unique=True, primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
            ('terms_of_service', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user_level', self.gf('django.db.models.fields.CharField')(max_length='6')),
            ('user_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal('institutions', ['PendingAccount'])

        # Adding unique constraint on 'PendingAccount', fields ['user_email', 'institution']
        db.create_unique('institutions_pendingaccount', ['user_email', 'institution_id'])

        # Adding model 'AccountInvite'
        db.create_table('institutions_accountinvite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('institutions', ['AccountInvite'])


    def backwards(self, orm):
        # Removing unique constraint on 'PendingAccount', fields ['user_email', 'institution']
        db.delete_unique('institutions_pendingaccount', ['user_email', 'institution_id'])

        # Removing unique constraint on 'StarsAccount', fields ['user', 'institution']
        db.delete_unique('institutions_starsaccount', ['user_id', 'institution_id'])

        # Deleting model 'ClimateZone'
        db.delete_table('institutions_climatezone')

        # Deleting model 'Institution'
        db.delete_table('institutions_institution')

        # Deleting model 'MigrationHistory'
        db.delete_table('institutions_migrationhistory')

        # Deleting model 'Subscription'
        db.delete_table('institutions_subscription')

        # Deleting model 'SubscriptionPayment'
        db.delete_table('institutions_subscriptionpayment')

        # Deleting model 'RegistrationReason'
        db.delete_table('institutions_registrationreason')

        # Deleting model 'RegistrationSurvey'
        db.delete_table('institutions_registrationsurvey')

        # Removing M2M table for field reasons on 'RegistrationSurvey'
        db.delete_table(db.shorten_name('institutions_registrationsurvey_reasons'))

        # Deleting model 'RespondentRegistrationReason'
        db.delete_table('institutions_respondentregistrationreason')

        # Deleting model 'RespondentSurvey'
        db.delete_table('institutions_respondentsurvey')

        # Removing M2M table for field reasons on 'RespondentSurvey'
        db.delete_table(db.shorten_name('institutions_respondentsurvey_reasons'))

        # Deleting model 'InstitutionPreferences'
        db.delete_table('institutions_institutionpreferences')

        # Deleting model 'BaseAccount'
        db.delete_table('institutions_baseaccount')

        # Deleting model 'StarsAccount'
        db.delete_table('institutions_starsaccount')

        # Deleting model 'PendingAccount'
        db.delete_table('institutions_pendingaccount')

        # Deleting model 'AccountInvite'
        db.delete_table('institutions_accountinvite')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'credits.creditset': {
            'Meta': {'ordering': "('release_date',)", 'object_name': 'CreditSet'},
            'credit_identifier': ('django.db.models.fields.CharField', [], {'default': "'get_1_1_identifier'", 'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.CreditSet']"}),
            'release_date': ('django.db.models.fields.DateField', [], {}),
            'scoring_method': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'supported_features': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['credits.IncrementalFeature']", 'symmetrical': 'False'}),
            'tier_2_points': ('django.db.models.fields.FloatField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'})
        },
        'credits.incrementalfeature': {
            'Meta': {'object_name': 'IncrementalFeature'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'credits.rating': {
            'Meta': {'ordering': "('-minimal_score',)", 'object_name': 'Rating'},
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_200': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_large': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'map_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'minimal_score': ('django.db.models.fields.SmallIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'16'"}),
            'publish_score': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'institutions.accountinvite': {
            'Meta': {'object_name': 'AccountInvite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'institutions.baseaccount': {
            'Meta': {'object_name': 'BaseAccount'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'institutions.climatezone': {
            'Meta': {'object_name': 'ClimateZone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'institutions.institution': {
            'Meta': {'object_name': 'Institution'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'charter_participant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'contact_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'contact_phone_ext': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'contact_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'current_rating': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Rating']", 'null': 'True', 'blank': 'True'}),
            'current_submission': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current'", 'null': 'True', 'to': "orm['submissions.SubmissionSet']"}),
            'current_subscription': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current'", 'null': 'True', 'to': "orm['institutions.Subscription']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'executive_contact_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'executive_contact_city': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'executive_contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'executive_contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'executive_contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'executive_contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'executive_contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'executive_contact_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'executive_contact_title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'executive_contact_zip': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'fte': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'international': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_member': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_participant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_pcc_signatory': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_pilot_participant': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'latest_expired_submission': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'latest_expired'", 'null': 'True', 'to': "orm['submissions.SubmissionSet']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'org_type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'prefers_metric_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'president_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'president_city': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'president_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'president_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'president_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'president_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'president_title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'president_zip': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'rated_submission': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rated'", 'null': 'True', 'to': "orm['submissions.SubmissionSet']"}),
            'rating_expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'stars_staff_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'institutions.institutionpreferences': {
            'Meta': {'object_name': 'InstitutionPreferences'},
            'institution': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'preferences'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['institutions.Institution']"}),
            'notify_users': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'institutions.migrationhistory': {
            'Meta': {'object_name': 'MigrationHistory'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'source_ss': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'migration_sources'", 'to': "orm['submissions.SubmissionSet']"}),
            'target_ss': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'migration_targets'", 'to': "orm['submissions.SubmissionSet']"})
        },
        'institutions.pendingaccount': {
            'Meta': {'unique_together': "(('user_email', 'institution'),)", 'object_name': 'PendingAccount'},
            'baseaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['institutions.BaseAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'terms_of_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'user_level': ('django.db.models.fields.CharField', [], {'max_length': "'6'"})
        },
        'institutions.registrationreason': {
            'Meta': {'object_name': 'RegistrationReason'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'institutions.registrationsurvey': {
            'Meta': {'object_name': 'RegistrationSurvey'},
            'enhancements': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'other': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'primary_reason': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'primary_surveys'", 'null': 'True', 'to': "orm['institutions.RegistrationReason']"}),
            'reasons': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['institutions.RegistrationReason']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'institutions.respondentregistrationreason': {
            'Meta': {'object_name': 'RespondentRegistrationReason'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'institutions.respondentsurvey': {
            'Meta': {'object_name': 'RespondentSurvey'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'other': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'potential_stars': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'reasons': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['institutions.RespondentRegistrationReason']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'institutions.starsaccount': {
            'Meta': {'unique_together': "(('user', 'institution'),)", 'object_name': 'StarsAccount'},
            'baseaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['institutions.BaseAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'is_selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'terms_of_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'user_level': ('django.db.models.fields.CharField', [], {'max_length': "'6'"})
        },
        'institutions.subscription': {
            'Meta': {'ordering': "['-start_date']", 'object_name': 'Subscription'},
            'amount_due': ('django.db.models.fields.FloatField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'late': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid_in_full': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ratings_allocated': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'ratings_used': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'institutions.subscriptionpayment': {
            'Meta': {'object_name': 'SubscriptionPayment'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': "'8'"}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Subscription']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'submissions.submissionset': {
            'Meta': {'ordering': "('date_registered',)", 'object_name': 'SubmissionSet'},
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'date_created': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_registered': ('django.db.models.fields.DateField', [], {}),
            'date_reviewed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_submitted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'migrated_from': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['submissions.SubmissionSet']"}),
            'pdf_report': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'presidents_letter': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Rating']", 'null': 'True', 'blank': 'True'}),
            'registering_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'registered_submissions'", 'to': "orm['auth.User']"}),
            'reporter_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'submission_boundary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'submitting_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submitted_submissions'", 'null': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['institutions']