# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'Category.previous_version'
        db.alter_column('credits_category', 'previous_version_id', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, unique=True, null=True, to=orm['credits.Category']))

        # Adding unique constraint on 'Category', fields ['previous_version']
        db.create_unique('credits_category', ['previous_version_id'])

        # Changing field 'Credit.previous_version'
        db.alter_column('credits_credit', 'previous_version_id', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, unique=True, null=True, to=orm['credits.Credit']))

        # Adding unique constraint on 'Credit', fields ['previous_version']
        db.create_unique('credits_credit', ['previous_version_id'])

        # Changing field 'ApplicabilityReason.previous_version'
        db.alter_column('credits_applicabilityreason', 'previous_version_id', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, unique=True, null=True, to=orm['credits.ApplicabilityReason']))

        # Adding unique constraint on 'ApplicabilityReason', fields ['previous_version']
        db.create_unique('credits_applicabilityreason', ['previous_version_id'])

        # Changing field 'Subcategory.previous_version'
        db.alter_column('credits_subcategory', 'previous_version_id', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, unique=True, null=True, to=orm['credits.Subcategory']))

        # Adding unique constraint on 'Subcategory', fields ['previous_version']
        db.create_unique('credits_subcategory', ['previous_version_id'])

        # Changing field 'Choice.previous_version'
        db.alter_column('credits_choice', 'previous_version_id', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, unique=True, null=True, to=orm['credits.Choice']))

        # Adding unique constraint on 'Choice', fields ['previous_version']
        db.create_unique('credits_choice', ['previous_version_id'])

        # Changing field 'DocumentationField.previous_version'
        db.alter_column('credits_documentationfield', 'previous_version_id', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, unique=True, null=True, to=orm['credits.DocumentationField']))

        # Adding unique constraint on 'DocumentationField', fields ['previous_version']
        db.create_unique('credits_documentationfield', ['previous_version_id'])

        # Changing field 'CreditSet.previous_version'
        db.alter_column('credits_creditset', 'previous_version_id', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, unique=True, null=True, to=orm['credits.CreditSet']))

        # Adding unique constraint on 'CreditSet', fields ['previous_version']
        db.create_unique('credits_creditset', ['previous_version_id'])
    
    
    def backwards(self, orm):
        
        # Changing field 'Category.previous_version'
        db.alter_column('credits_category', 'previous_version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Category'], null=True, blank=True))

        # Removing unique constraint on 'Category', fields ['previous_version']
        db.delete_unique('credits_category', ['previous_version_id'])

        # Changing field 'Credit.previous_version'
        db.alter_column('credits_credit', 'previous_version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Credit'], null=True, blank=True))

        # Removing unique constraint on 'Credit', fields ['previous_version']
        db.delete_unique('credits_credit', ['previous_version_id'])

        # Changing field 'ApplicabilityReason.previous_version'
        db.alter_column('credits_applicabilityreason', 'previous_version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.ApplicabilityReason'], null=True, blank=True))

        # Removing unique constraint on 'ApplicabilityReason', fields ['previous_version']
        db.delete_unique('credits_applicabilityreason', ['previous_version_id'])

        # Changing field 'Subcategory.previous_version'
        db.alter_column('credits_subcategory', 'previous_version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Subcategory'], null=True, blank=True))

        # Removing unique constraint on 'Subcategory', fields ['previous_version']
        db.delete_unique('credits_subcategory', ['previous_version_id'])

        # Changing field 'Choice.previous_version'
        db.alter_column('credits_choice', 'previous_version_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['credits.Choice'], blank=True))

        # Removing unique constraint on 'Choice', fields ['previous_version']
        db.delete_unique('credits_choice', ['previous_version_id'])

        # Changing field 'DocumentationField.previous_version'
        db.alter_column('credits_documentationfield', 'previous_version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.DocumentationField'], null=True, blank=True))

        # Removing unique constraint on 'DocumentationField', fields ['previous_version']
        db.delete_unique('credits_documentationfield', ['previous_version_id'])

        # Changing field 'CreditSet.previous_version'
        db.alter_column('credits_creditset', 'previous_version_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.CreditSet'], null=True, blank=True))

        # Removing unique constraint on 'CreditSet', fields ['previous_version']
        db.delete_unique('credits_creditset', ['previous_version_id'])
    
    
    models = {
        'credits.applicabilityreason': {
            'Meta': {'object_name': 'ApplicabilityReason'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.ApplicabilityReason']"}),
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
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Category']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'credits.choice': {
            'Meta': {'object_name': 'Choice'},
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_bonafide': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Choice']"})
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
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Credit']"}),
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
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.CreditSet']"}),
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
            'last_choice_is_other': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'max_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.DocumentationField']"}),
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
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Subcategory']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'credits.unit': {
            'Meta': {'object_name': 'Unit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }
    
    complete_apps = ['credits']
