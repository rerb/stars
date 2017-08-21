# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting model 'SubcategoryQuartiles'
        db.delete_table('submissions_subcategoryquartiles')


    def backwards(self, orm):
        # Adding model 'SubcategoryQuartiles'
        db.create_table('submissions_subcategoryquartiles', (
            ('org_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('second', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('subcategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Subcategory'])),
            ('fourth', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('third', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('submissions', ['SubcategoryQuartiles'])

        # Adding unique constraint on 'SubcategoryQuartiles', fields ['subcategory', 'org_type']
        db.create_unique('submissions_subcategoryquartiles', ['subcategory_id', 'org_type'])


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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'credits.applicabilityreason': {
            'Meta': {'ordering': "('ordinal',)", 'object_name': 'ApplicabilityReason'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.ApplicabilityReason']"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'credits.category': {
            'Meta': {'ordering': "('ordinal',)", 'object_name': 'Category'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_in_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'include_in_score': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'max_point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Category']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'credits.choice': {
            'Meta': {'ordering': "('ordinal',)", 'object_name': 'Choice'},
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_bonafide': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Choice']"})
        },
        'credits.credit': {
            'Meta': {'ordering': "('ordinal',)", 'object_name': 'Credit'},
            'applicability': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'criteria': ('django.db.models.fields.TextField', [], {}),
            'formula': ('django.db.models.fields.TextField', [], {'default': "'points = 0'", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'default': "'ID?'", 'max_length': '16', 'db_index': 'True'}),
            'is_opt_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'measurement': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1', 'db_index': 'True'}),
            'point_minimum': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'point_value': ('django.db.models.fields.FloatField', [], {}),
            'point_value_formula': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'point_variation_reason': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Credit']"}),
            'resources': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'scoring': ('django.db.models.fields.TextField', [], {}),
            'show_info': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'staff_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Subcategory']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'validation_rules': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
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
        'credits.documentationfield': {
            'Meta': {'ordering': "('ordinal',)", 'unique_together': "(('credit', 'identifier'),)", 'object_name': 'DocumentationField'},
            'copy_from_field': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'source_field'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['credits.DocumentationField']"}),
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'formula': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'formula_terms': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'calculated_fields'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['credits.DocumentationField']"}),
            'header': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'imperial_formula_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'inline_help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_choice_is_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'metric_formula_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'min_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1', 'db_index': 'True'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.DocumentationField']"}),
            'required': ('django.db.models.fields.CharField', [], {'default': "'req'", 'max_length': '8'}),
            'tabular_fields': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tooltip_help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'}),
            'units': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Unit']", 'null': 'True', 'blank': 'True'})
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
        'credits.subcategory': {
            'Meta': {'ordering': "('category', 'ordinal')", 'object_name': 'Subcategory'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'passthrough': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Subcategory']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'credits.unit': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Unit'},
            'equivalent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Unit']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_metric': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'ratio': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'null': 'True', 'blank': 'True'})
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
            'contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'contact_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'contact_phone_ext': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'contact_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'current_rating': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Rating']", 'null': 'True', 'blank': 'True'}),
            'current_submission': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current'", 'null': 'True', 'to': "orm['submissions.SubmissionSet']"}),
            'current_subscription': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current'", 'null': 'True', 'to': "orm['institutions.Subscription']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
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
            'institution_type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'international': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_member': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_pcc_signatory': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_pilot_participant': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'latest_expired_submission': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'latest_expired'", 'null': 'True', 'to': "orm['submissions.SubmissionSet']"}),
            'ms_institution': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['iss.Organization']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'prefers_metric_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'president_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'president_city': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'president_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
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
        'institutions.subscription': {
            'Meta': {'ordering': "['-start_date']", 'object_name': 'Subscription'},
            'access_level': ('django.db.models.fields.CharField', [], {'default': "'Basic'", 'max_length': '8'}),
            'amount_due': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'late': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ms_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'ms_institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['iss.Organization']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'paid_in_full': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ratings_allocated': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'ratings_used': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'})
        },
        'iss.organization': {
            'Meta': {'object_name': 'Organization'},
            'account_num': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'business_member_level': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'carnegie_class': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'class_profile': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country_iso': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'enrollment_fte': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exclude_from_website': ('django.db.models.fields.IntegerField', [], {}),
            'institution_type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'is_defunct': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'is_member': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'is_signatory': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'member_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'membersuite_account_num': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'membersuite_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'org_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'org_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['iss.OrganizationType']", 'null': 'True'}),
            'picklist_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pilot_participant': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'primary_email': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'salesforce_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sector': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'setting': ('django.db.models.fields.CharField', [], {'max_length': '33', 'null': 'True', 'blank': 'True'}),
            'stars_participant_status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'street1': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'street2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sustainability_website': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'iss.organizationtype': {
            'Meta': {'object_name': 'OrganizationType'},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'submissions.booleansubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'BooleanSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'booleansubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.boundary': {
            'Meta': {'object_name': 'Boundary'},
            'additional_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ag_school_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ag_school_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'ag_school_present': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'agr_exp_acres': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'agr_exp_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'agr_exp_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'agr_exp_present': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'climate_region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.ClimateZone']", 'null': 'True', 'blank': 'True'}),
            'cultivated_grounds_acres': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'endowment_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'farm_acres': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'farm_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'farm_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'farm_present': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'fte_employmees': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'fte_students': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'graduate_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'gsf_building_space': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'gsf_lab_space': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'hospital_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hospital_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'hospital_present': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution_type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'institutional_control': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'med_school_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'med_school_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'med_school_present': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'pharm_school_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pharm_school_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'pharm_school_present': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'pub_health_school_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pub_health_school_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'pub_health_school_present': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'sat_campus_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sat_campus_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'sat_campus_present': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'student_ftc_percent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student_online_percent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student_ptc_percent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student_residential_percent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'submissionset': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.SubmissionSet']", 'unique': 'True'}),
            'undergrad_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'undeveloped_land_acres': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'vet_school_details': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'vet_school_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'vet_school_present': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.categorysubmission': {
            'Meta': {'ordering': "('category__ordinal',)", 'unique_together': "(('submissionset', 'category'),)", 'object_name': 'CategorySubmission'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
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
            'Meta': {'ordering': "('credit__type', 'credit__ordinal')", 'object_name': 'CreditSubmission'},
            'available_point_cache': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_unlocked_for_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'submissions.creditsubmissioninquiry': {
            'Meta': {'object_name': 'CreditSubmissionInquiry'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'explanation': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission_inquiry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionInquiry']"})
        },
        'submissions.creditsubmissionreviewnotation': {
            'Meta': {'ordering': "('kind', 'credit_user_submission__credit__identifier', 'id')", 'object_name': 'CreditSubmissionReviewNotation'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'credit_user_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditUserSubmission']"}),
            'email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': "'32'"}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'submissions.credittestsubmission': {
            'Meta': {'ordering': "('credit__type', 'credit__ordinal')", 'object_name': 'CreditTestSubmission', '_ormbases': ['submissions.CreditSubmission']},
            'creditsubmission_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.CreditSubmission']", 'unique': 'True', 'primary_key': 'True'}),
            'expected_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.creditusersubmission': {
            'Meta': {'ordering': "('credit__type', 'credit__ordinal')", 'object_name': 'CreditUserSubmission', '_ormbases': ['submissions.CreditSubmission']},
            'applicability_reason': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.ApplicabilityReason']", 'null': 'True', 'blank': 'True'}),
            'assessed_points': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'creditsubmission_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.CreditSubmission']", 'unique': 'True', 'primary_key': 'True'}),
            'internal_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'responsible_party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.ResponsibleParty']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'responsible_party_confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'review_conclusion': ('django.db.models.fields.CharField', [], {'default': "'not-reviewed'", 'max_length': '32'}),
            'subcategory_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubcategorySubmission']"}),
            'submission_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'submission_status': ('django.db.models.fields.CharField', [], {'default': "'ns'", 'max_length': '8'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'submissions.datacorrectionrequest': {
            'Meta': {'object_name': 'DataCorrectionRequest'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'explanation': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_value': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'submissions.datesubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'DateSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datesubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.extensionrequest': {
            'Meta': {'object_name': 'ExtensionRequest'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_deadline': ('django.db.models.fields.DateField', [], {}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionSet']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'submissions.flag': {
            'Meta': {'object_name': 'Flag'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
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
            'metric_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'16'"}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionSet']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': "'8'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'submissions.reportingfielddatacorrection': {
            'Meta': {'object_name': 'ReportingFieldDataCorrection'},
            'change_date': ('django.db.models.fields.DateField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'explanation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'previous_value': ('django.db.models.fields.TextField', [], {}),
            'request': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'applied_correction'", 'unique': 'True', 'null': 'True', 'to': "orm['submissions.DataCorrectionRequest']"})
        },
        'submissions.responsibleparty': {
            'Meta': {'ordering': "('last_name', 'first_name')", 'object_name': 'ResponsibleParty'},
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
            'Meta': {'ordering': "('subcategory__ordinal',)", 'unique_together': "(('category_submission', 'subcategory'),)", 'object_name': 'SubcategorySubmission'},
            'adjusted_available_points': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'category_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CategorySubmission']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percentage_score': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'points': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Subcategory']"})
        },
        'submissions.submissioninquiry': {
            'Meta': {'object_name': 'SubmissionInquiry'},
            'additional_comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionSet']"})
        },
        'submissions.submissionset': {
            'Meta': {'ordering': "('date_registered',)", 'object_name': 'SubmissionSet'},
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
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
