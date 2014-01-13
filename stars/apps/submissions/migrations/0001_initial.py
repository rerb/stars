# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'SubmissionSet'
        db.create_table('submissions_submissionset', (
            ('status', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('rating', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Rating'], null=True, blank=True)),
            ('submission_boundary', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('submission_deadline', self.gf('django.db.models.fields.DateField')()),
            ('submitting_user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='submitted_submissions', null=True, to=orm['auth.User'])),
            ('creditset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.CreditSet'])),
            ('presidents_letter', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('date_submitted', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
            ('date_registered', self.gf('django.db.models.fields.DateField')()),
            ('date_reviewed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('reporter_status', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('registering_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='registered_submissions', to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('submissions', ['SubmissionSet'])

        # Adding model 'CategorySubmission'
        db.create_table('submissions_categorysubmission', (
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Category'])),
            ('submissionset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.SubmissionSet'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('submissions', ['CategorySubmission'])

        # Adding unique constraint on 'CategorySubmission', fields ['submissionset', 'category']
        db.create_unique('submissions_categorysubmission', ['submissionset_id', 'category_id'])

        # Adding model 'SubcategorySubmission'
        db.create_table('submissions_subcategorysubmission', (
            ('category_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.CategorySubmission'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subcategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Subcategory'])),
        ))
        db.send_create_signal('submissions', ['SubcategorySubmission'])

        # Adding unique constraint on 'SubcategorySubmission', fields ['category_submission', 'subcategory']
        db.create_unique('submissions_subcategorysubmission', ['category_submission_id', 'subcategory_id'])

        # Adding model 'ResponsibleParty'
        db.create_table('submissions_responsibleparty', (
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['institutions.Institution'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('department', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('submissions', ['ResponsibleParty'])

        # Adding model 'CreditSubmission'
        db.create_table('submissions_creditsubmission', (
            ('credit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Credit'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('submissions', ['CreditSubmission'])

        # Adding model 'CreditUserSubmission'
        db.create_table('submissions_creditusersubmission', (
            ('creditsubmission_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['submissions.CreditSubmission'], unique=True, primary_key=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('responsible_party_confirm', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('submission_notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('internal_notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('review_status', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('submission_status', self.gf('django.db.models.fields.CharField')(default='ns', max_length=8)),
            ('responsible_party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.ResponsibleParty'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('assessed_points', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('subcategory_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.SubcategorySubmission'])),
            ('applicability_reason', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.ApplicabilityReason'], null=True, blank=True)),
        ))
        db.send_create_signal('submissions', ['CreditUserSubmission'])

        # Adding model 'CreditTestSubmission'
        db.create_table('submissions_credittestsubmission', (
            ('creditsubmission_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['submissions.CreditSubmission'], unique=True, primary_key=True)),
            ('expected_value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('submissions', ['CreditTestSubmission'])

        # Adding model 'ChoiceSubmission'
        db.create_table('submissions_choicesubmission', (
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='choicesubmission_set', to=orm['credits.DocumentationField'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Choice'], null=True, blank=True)),
            ('credit_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.CreditSubmission'])),
        ))
        db.send_create_signal('submissions', ['ChoiceSubmission'])

        # Adding model 'MultiChoiceSubmission'
        db.create_table('submissions_multichoicesubmission', (
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='multichoicesubmission_set', to=orm['credits.DocumentationField'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('credit_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.CreditSubmission'])),
        ))
        db.send_create_signal('submissions', ['MultiChoiceSubmission'])

        # Adding M2M table for field value on 'MultiChoiceSubmission'
        db.create_table('submissions_multichoicesubmission_value', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('multichoicesubmission', models.ForeignKey(orm['submissions.multichoicesubmission'], null=False)),
            ('choice', models.ForeignKey(orm['credits.choice'], null=False))
        ))
        db.create_unique('submissions_multichoicesubmission_value', ['multichoicesubmission_id', 'choice_id'])

        # Adding model 'URLSubmission'
        db.create_table('submissions_urlsubmission', (
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='urlsubmission_set', to=orm['credits.DocumentationField'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('credit_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.CreditSubmission'])),
        ))
        db.send_create_signal('submissions', ['URLSubmission'])

        # Adding unique constraint on 'URLSubmission', fields ['documentation_field', 'credit_submission']
        db.create_unique('submissions_urlsubmission', ['documentation_field_id', 'credit_submission_id'])

        # Adding model 'DateSubmission'
        db.create_table('submissions_datesubmission', (
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datesubmission_set', to=orm['credits.DocumentationField'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('credit_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.CreditSubmission'])),
        ))
        db.send_create_signal('submissions', ['DateSubmission'])

        # Adding unique constraint on 'DateSubmission', fields ['documentation_field', 'credit_submission']
        db.create_unique('submissions_datesubmission', ['documentation_field_id', 'credit_submission_id'])

        # Adding model 'NumericSubmission'
        db.create_table('submissions_numericsubmission', (
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='numericsubmission_set', to=orm['credits.DocumentationField'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('credit_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.CreditSubmission'])),
        ))
        db.send_create_signal('submissions', ['NumericSubmission'])

        # Adding unique constraint on 'NumericSubmission', fields ['documentation_field', 'credit_submission']
        db.create_unique('submissions_numericsubmission', ['documentation_field_id', 'credit_submission_id'])

        # Adding model 'TextSubmission'
        db.create_table('submissions_textsubmission', (
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='textsubmission_set', to=orm['credits.DocumentationField'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('credit_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.CreditSubmission'])),
        ))
        db.send_create_signal('submissions', ['TextSubmission'])

        # Adding unique constraint on 'TextSubmission', fields ['documentation_field', 'credit_submission']
        db.create_unique('submissions_textsubmission', ['documentation_field_id', 'credit_submission_id'])

        # Adding model 'LongTextSubmission'
        db.create_table('submissions_longtextsubmission', (
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='longtextsubmission_set', to=orm['credits.DocumentationField'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('credit_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.CreditSubmission'])),
        ))
        db.send_create_signal('submissions', ['LongTextSubmission'])

        # Adding unique constraint on 'LongTextSubmission', fields ['documentation_field', 'credit_submission']
        db.create_unique('submissions_longtextsubmission', ['documentation_field_id', 'credit_submission_id'])

        # Adding model 'UploadSubmission'
        db.create_table('submissions_uploadsubmission', (
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='uploadsubmission_set', to=orm['credits.DocumentationField'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('credit_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.CreditSubmission'])),
        ))
        db.send_create_signal('submissions', ['UploadSubmission'])

        # Adding unique constraint on 'UploadSubmission', fields ['documentation_field', 'credit_submission']
        db.create_unique('submissions_uploadsubmission', ['documentation_field_id', 'credit_submission_id'])

        # Adding model 'BooleanSubmission'
        db.create_table('submissions_booleansubmission', (
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='booleansubmission_set', to=orm['credits.DocumentationField'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('credit_submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.CreditSubmission'])),
        ))
        db.send_create_signal('submissions', ['BooleanSubmission'])

        # Adding unique constraint on 'BooleanSubmission', fields ['documentation_field', 'credit_submission']
        db.create_unique('submissions_booleansubmission', ['documentation_field_id', 'credit_submission_id'])

        # Adding model 'Payment'
        db.create_table('submissions_payment', (
            ('confirmation', self.gf('django.db.models.fields.CharField')(max_length='16', null=True, blank=True)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length='8')),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('submissionset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.SubmissionSet'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length='8')),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('submissions', ['Payment'])

        # Adding model 'SubmissionEnquiry'
        db.create_table('submissions_submissionenquiry', (
            ('phone_number', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('affiliation', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('submissionset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.SubmissionSet'])),
            ('email_address', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('addtional_comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('submissions', ['SubmissionEnquiry'])

        # Adding model 'CreditSubmissionEnquiry'
        db.create_table('submissions_creditsubmissionenquiry', (
            ('submission_enquiry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['submissions.SubmissionEnquiry'])),
            ('credit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Credit'])),
            ('explanation', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('submissions', ['CreditSubmissionEnquiry'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'SubmissionSet'
        db.delete_table('submissions_submissionset')

        # Deleting model 'CategorySubmission'
        db.delete_table('submissions_categorysubmission')

        # Removing unique constraint on 'CategorySubmission', fields ['submissionset', 'category']
        db.delete_unique('submissions_categorysubmission', ['submissionset_id', 'category_id'])

        # Deleting model 'SubcategorySubmission'
        db.delete_table('submissions_subcategorysubmission')

        # Removing unique constraint on 'SubcategorySubmission', fields ['category_submission', 'subcategory']
        db.delete_unique('submissions_subcategorysubmission', ['category_submission_id', 'subcategory_id'])

        # Deleting model 'ResponsibleParty'
        db.delete_table('submissions_responsibleparty')

        # Deleting model 'CreditSubmission'
        db.delete_table('submissions_creditsubmission')

        # Deleting model 'CreditUserSubmission'
        db.delete_table('submissions_creditusersubmission')

        # Deleting model 'CreditTestSubmission'
        db.delete_table('submissions_credittestsubmission')

        # Deleting model 'ChoiceSubmission'
        db.delete_table('submissions_choicesubmission')

        # Deleting model 'MultiChoiceSubmission'
        db.delete_table('submissions_multichoicesubmission')

        # Removing M2M table for field value on 'MultiChoiceSubmission'
        db.delete_table('submissions_multichoicesubmission_value')

        # Deleting model 'URLSubmission'
        db.delete_table('submissions_urlsubmission')

        # Removing unique constraint on 'URLSubmission', fields ['documentation_field', 'credit_submission']
        db.delete_unique('submissions_urlsubmission', ['documentation_field_id', 'credit_submission_id'])

        # Deleting model 'DateSubmission'
        db.delete_table('submissions_datesubmission')

        # Removing unique constraint on 'DateSubmission', fields ['documentation_field', 'credit_submission']
        db.delete_unique('submissions_datesubmission', ['documentation_field_id', 'credit_submission_id'])

        # Deleting model 'NumericSubmission'
        db.delete_table('submissions_numericsubmission')

        # Removing unique constraint on 'NumericSubmission', fields ['documentation_field', 'credit_submission']
        db.delete_unique('submissions_numericsubmission', ['documentation_field_id', 'credit_submission_id'])

        # Deleting model 'TextSubmission'
        db.delete_table('submissions_textsubmission')

        # Removing unique constraint on 'TextSubmission', fields ['documentation_field', 'credit_submission']
        db.delete_unique('submissions_textsubmission', ['documentation_field_id', 'credit_submission_id'])

        # Deleting model 'LongTextSubmission'
        db.delete_table('submissions_longtextsubmission')

        # Removing unique constraint on 'LongTextSubmission', fields ['documentation_field', 'credit_submission']
        db.delete_unique('submissions_longtextsubmission', ['documentation_field_id', 'credit_submission_id'])

        # Deleting model 'UploadSubmission'
        db.delete_table('submissions_uploadsubmission')

        # Removing unique constraint on 'UploadSubmission', fields ['documentation_field', 'credit_submission']
        db.delete_unique('submissions_uploadsubmission', ['documentation_field_id', 'credit_submission_id'])

        # Deleting model 'BooleanSubmission'
        db.delete_table('submissions_booleansubmission')

        # Removing unique constraint on 'BooleanSubmission', fields ['documentation_field', 'credit_submission']
        db.delete_unique('submissions_booleansubmission', ['documentation_field_id', 'credit_submission_id'])

        # Deleting model 'Payment'
        db.delete_table('submissions_payment')

        # Deleting model 'SubmissionEnquiry'
        db.delete_table('submissions_submissionenquiry')

        # Deleting model 'CreditSubmissionEnquiry'
        db.delete_table('submissions_creditsubmissionenquiry')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'credits.applicabilityreason': {
            'Meta': {'object_name': 'ApplicabilityReason'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'credits.category': {
            'Meta': {'object_name': 'Category'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'credits.choice': {
            'Meta': {'object_name': 'Choice'},
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_bonafide': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'})
        },
        'credits.credit': {
            'Meta': {'object_name': 'Credit'},
            'applicability': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'criteria': ('django.db.models.fields.TextField', [], {}),
            'formula': ('django.db.models.fields.TextField', [], {'default': "'points = 0'", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurement': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'point_value': ('django.db.models.fields.FloatField', [], {}),
            'scoring': ('django.db.models.fields.TextField', [], {}),
            'staff_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Subcategory']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'validation_rules': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
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
        'credits.documentationfield': {
            'Meta': {'unique_together': "(('credit', 'identifier'),)", 'object_name': 'DocumentationField'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'inline_help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'is_confidential': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_choice_is_other': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'max_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'required': ('django.db.models.fields.CharField', [], {'default': "'req'", 'max_length': '8'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tooltip_help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'units': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Unit']", 'null': 'True', 'blank': 'True'})
        },
        'credits.rating': {
            'Meta': {'object_name': 'Rating'},
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_200': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_large': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'minimal_score': ('django.db.models.fields.SmallIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'16'"})
        },
        'credits.subcategory': {
            'Meta': {'object_name': 'Subcategory'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'credits.unit': {
            'Meta': {'object_name': 'Unit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
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
            'contact_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'contact_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'executive_contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'executive_contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'executive_contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'executive_contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'executive_contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'executive_contact_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'submissions.booleansubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'BooleanSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'booleansubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.categorysubmission': {
            'Meta': {'unique_together': "(('submissionset', 'category'),)", 'object_name': 'CategorySubmission'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionSet']"})
        },
        'submissions.choicesubmission': {
            'Meta': {'object_name': 'ChoiceSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'choicesubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Choice']", 'null': 'True', 'blank': 'True'})
        },
        'submissions.creditsubmission': {
            'Meta': {'object_name': 'CreditSubmission'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'submissions.creditsubmissionenquiry': {
            'Meta': {'object_name': 'CreditSubmissionEnquiry'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'explanation': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission_enquiry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionEnquiry']"})
        },
        'submissions.credittestsubmission': {
            'Meta': {'object_name': 'CreditTestSubmission', '_ormbases': ['submissions.CreditSubmission']},
            'creditsubmission_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.CreditSubmission']", 'unique': 'True', 'primary_key': 'True'}),
            'expected_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.creditusersubmission': {
            'Meta': {'object_name': 'CreditUserSubmission', '_ormbases': ['submissions.CreditSubmission']},
            'applicability_reason': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.ApplicabilityReason']", 'null': 'True', 'blank': 'True'}),
            'assessed_points': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'creditsubmission_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.CreditSubmission']", 'unique': 'True', 'primary_key': 'True'}),
            'internal_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'responsible_party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.ResponsibleParty']", 'null': 'True', 'blank': 'True'}),
            'responsible_party_confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'review_status': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'subcategory_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubcategorySubmission']"}),
            'submission_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'submission_status': ('django.db.models.fields.CharField', [], {'default': "'ns'", 'max_length': '8'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'submissions.datesubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'DateSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datesubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.longtextsubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'LongTextSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'longtextsubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.multichoicesubmission': {
            'Meta': {'object_name': 'MultiChoiceSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'multichoicesubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['credits.Choice']", 'null': 'True', 'blank': 'True'})
        },
        'submissions.numericsubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'NumericSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'numericsubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'8'"}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionSet']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': "'8'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'submissions.responsibleparty': {
            'Meta': {'object_name': 'ResponsibleParty'},
            'department': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'submissions.subcategorysubmission': {
            'Meta': {'unique_together': "(('category_submission', 'subcategory'),)", 'object_name': 'SubcategorySubmission'},
            'category_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CategorySubmission']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Subcategory']"})
        },
        'submissions.submissionenquiry': {
            'Meta': {'object_name': 'SubmissionEnquiry'},
            'addtional_comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionSet']"})
        },
        'submissions.submissionset': {
            'Meta': {'object_name': 'SubmissionSet'},
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
        },
        'submissions.textsubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'TextSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'textsubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'submissions.uploadsubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'UploadSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'uploadsubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'submissions.urlsubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'URLSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'urlsubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['submissions']
