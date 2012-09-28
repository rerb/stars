# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Institution'
        db.create_table('institutions_institution', (
            ('executive_contact_department', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='255')),
            ('contact_last_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('executive_contact_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('charter_participant', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('executive_contact_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('executive_contact_first_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('contact_department', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('contact_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('contact_first_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('executive_contact_title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('contact_title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('contact_phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')()),
            ('contact_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('executive_contact_last_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('institutions', ['Institution'])

        # Adding model 'RegistrationReason'
        db.create_table('institutions_registrationreason', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('institutions', ['RegistrationReason'])

        # Adding model 'RegistrationSurvey'
        db.create_table('institutions_registrationsurvey', (
            ('primary_reason', self.gf('django.db.models.fields.related.ForeignKey')(related_name='primary_surveys', to=orm['institutions.RegistrationReason'])),
            ('enhancements', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
            ('source', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('institutions', ['RegistrationSurvey'])

        # Adding M2M table for field reasons on 'RegistrationSurvey'
        db.create_table('institutions_registrationsurvey_reasons', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('registrationsurvey', models.ForeignKey(orm['institutions.registrationsurvey'], null=False)),
            ('registrationreason', models.ForeignKey(orm['institutions.registrationreason'], null=False))
        ))
        db.create_unique('institutions_registrationsurvey_reasons', ['registrationsurvey_id', 'registrationreason_id'])

        # Adding model 'InstitutionState'
        db.create_table('institutions_institutionstate', (
            ('active_submission_set', self.gf('django.db.models.fields.related.ForeignKey')(related_name='active_submission', to=orm['submissions.SubmissionSet'])),
            ('latest_rated_submission_set', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='rated_submission', null=True, blank=True, to=orm['submissions.SubmissionSet'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('institution', self.gf('django.db.models.fields.related.OneToOneField')(related_name='state', unique=True, to=orm['institutions.Institution'])),
        ))
        db.send_create_signal('institutions', ['InstitutionState'])

        # Adding model 'InstitutionPreferences'
        db.create_table('institutions_institutionpreferences', (
            ('notify_users', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('institution', self.gf('django.db.models.fields.related.OneToOneField')(related_name='preferences', unique=True, primary_key=True, to=orm['institutions.Institution'])),
        ))
        db.send_create_signal('institutions', ['InstitutionPreferences'])

        # Adding model 'BaseAccount'
        db.create_table('institutions_baseaccount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('institutions', ['BaseAccount'])

        # Adding model 'StarsAccount'
        db.create_table('institutions_starsaccount', (
            ('baseaccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['institutions.BaseAccount'], unique=True)),
            ('is_selected', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('user_level', self.gf('django.db.models.fields.CharField')(max_length='6')),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('terms_of_service', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
        ))
        db.send_create_signal('institutions', ['StarsAccount'])

        # Adding unique constraint on 'StarsAccount', fields ['user', 'institution']
        db.create_unique('institutions_starsaccount', ['user_id', 'institution_id'])

        # Adding model 'PendingAccount'
        db.create_table('institutions_pendingaccount', (
            ('baseaccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['institutions.BaseAccount'], unique=True, primary_key=True)),
            ('user_level', self.gf('django.db.models.fields.CharField')(max_length='6')),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
            ('user_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('terms_of_service', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
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
        
        # Deleting model 'Institution'
        db.delete_table('institutions_institution')

        # Deleting model 'RegistrationReason'
        db.delete_table('institutions_registrationreason')

        # Deleting model 'RegistrationSurvey'
        db.delete_table('institutions_registrationsurvey')

        # Removing M2M table for field reasons on 'RegistrationSurvey'
        db.delete_table('institutions_registrationsurvey_reasons')

        # Deleting model 'InstitutionState'
        db.delete_table('institutions_institutionstate')

        # Deleting model 'InstitutionPreferences'
        db.delete_table('institutions_institutionpreferences')

        # Deleting model 'BaseAccount'
        db.delete_table('institutions_baseaccount')

        # Deleting model 'StarsAccount'
        db.delete_table('institutions_starsaccount')

        # Removing unique constraint on 'StarsAccount', fields ['user', 'institution']
        db.delete_unique('institutions_starsaccount', ['user_id', 'institution_id'])

        # Deleting model 'PendingAccount'
        db.delete_table('institutions_pendingaccount')

        # Removing unique constraint on 'PendingAccount', fields ['user_email', 'institution']
        db.delete_unique('institutions_pendingaccount', ['user_email', 'institution_id'])

        # Deleting model 'AccountInvite'
        db.delete_table('institutions_accountinvite')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'credits.creditset': {
            'Meta': {'object_name': 'CreditSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'release_date': ('django.db.models.fields.DateField', [], {}),
            'scoring_method': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'tier_2_points': ('django.db.models.fields.FloatField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'})
        },
        'credits.rating': {
            'Meta': {'object_name': 'Rating'},
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimal_score': ('django.db.models.fields.SmallIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'16'"})
        },
        'institutions.accountinvite': {
            'Meta': {'object_name': 'AccountInvite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'institutions.baseaccount': {
            'Meta': {'object_name': 'BaseAccount'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'institutions.institution': {
            'Meta': {'object_name': 'Institution'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'charter_participant': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'contact_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {}),
            'contact_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'executive_contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'executive_contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'executive_contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'executive_contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'executive_contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'executive_contact_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'255'"})
        },
        'institutions.institutionpreferences': {
            'Meta': {'object_name': 'InstitutionPreferences'},
            'institution': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'preferences'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['institutions.Institution']"}),
            'notify_users': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'institutions.institutionstate': {
            'Meta': {'object_name': 'InstitutionState'},
            'active_submission_set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'active_submission'", 'to': "orm['submissions.SubmissionSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'state'", 'unique': 'True', 'to': "orm['institutions.Institution']"}),
            'latest_rated_submission_set': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'rated_submission'", 'null': 'True', 'blank': 'True', 'to': "orm['submissions.SubmissionSet']"})
        },
        'institutions.pendingaccount': {
            'Meta': {'unique_together': "(('user_email', 'institution'),)", 'object_name': 'PendingAccount'},
            'baseaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['institutions.BaseAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'terms_of_service': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
            'primary_reason': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'primary_surveys'", 'to': "orm['institutions.RegistrationReason']"}),
            'reasons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['institutions.RegistrationReason']"}),
            'source': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'institutions.starsaccount': {
            'Meta': {'unique_together': "(('user', 'institution'),)", 'object_name': 'StarsAccount'},
            'baseaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['institutions.BaseAccount']", 'unique': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'is_selected': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'terms_of_service': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'user_level': ('django.db.models.fields.CharField', [], {'max_length': "'6'"})
        },
        'submissions.submissionset': {
            'Meta': {'unique_together': "(('institution', 'creditset'),)", 'object_name': 'SubmissionSet'},
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'date_registered': ('django.db.models.fields.DateField', [], {}),
            'date_reviewed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_submitted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'presidents_letter': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Rating']", 'null': 'True', 'blank': 'True'}),
            'registering_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'registered_submissions'", 'to': "orm['auth.User']"}),
            'reporter_status': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'submission_boundary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'submission_deadline': ('django.db.models.fields.DateField', [], {}),
            'submitting_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submitted_submissions'", 'null': 'True', 'to': "orm['auth.User']"})
        }
    }
    
    complete_apps = ['institutions']
