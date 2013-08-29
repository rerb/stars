# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'CreditSet'
        db.create_table('credits_creditset', (
            ('is_locked', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('tier_2_points', self.gf('django.db.models.fields.FloatField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.CharField')(unique=True, max_length=5)),
            ('scoring_method', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('release_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('credits', ['CreditSet'])

        # Adding model 'Rating'
        db.create_table('credits_rating', (
            ('creditset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.CreditSet'])),
            ('minimal_score', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='16')),
        ))
        db.send_create_signal('credits', ['Rating'])

        # Adding model 'Category'
        db.create_table('credits_category', (
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('creditset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.CreditSet'])),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('max_point_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('credits', ['Category'])

        # Adding model 'Subcategory'
        db.create_table('credits_subcategory', (
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Category'])),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('max_point_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('credits', ['Subcategory'])

        # Adding model 'Credit'
        db.create_table('credits_credit', (
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('scoring', self.gf('django.db.models.fields.TextField')()),
            ('staff_notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('subcategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Subcategory'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('criteria', self.gf('django.db.models.fields.TextField')()),
            ('measurement', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('point_value', self.gf('django.db.models.fields.FloatField')()),
            ('applicability', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('validation_rules', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('formula', self.gf('django.db.models.fields.TextField')(default='points = 0', null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('credits', ['Credit'])

        # Adding model 'ApplicabilityReason'
        db.create_table('credits_applicabilityreason', (
            ('help_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Credit'])),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('credits', ['ApplicabilityReason'])

        # Adding model 'Unit'
        db.create_table('credits_unit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('credits', ['Unit'])

        # Adding model 'DocumentationField'
        db.create_table('credits_documentationfield', (
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('max_range', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_confidential', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('required', self.gf('django.db.models.fields.CharField')(default='req', max_length=8)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tooltip_help_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('last_choice_is_other', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('min_range', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Credit'])),
            ('inline_help_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('units', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Unit'], null=True, blank=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('credits', ['DocumentationField'])

        # Adding unique constraint on 'DocumentationField', fields ['credit', 'identifier']
        db.create_unique('credits_documentationfield', ['credit_id', 'identifier'])

        # Adding model 'Choice'
        db.create_table('credits_choice', (
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.DocumentationField'])),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('is_bonafide', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('choice', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('credits', ['Choice'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'CreditSet'
        db.delete_table('credits_creditset')

        # Deleting model 'Rating'
        db.delete_table('credits_rating')

        # Deleting model 'Category'
        db.delete_table('credits_category')

        # Deleting model 'Subcategory'
        db.delete_table('credits_subcategory')

        # Deleting model 'Credit'
        db.delete_table('credits_credit')

        # Deleting model 'ApplicabilityReason'
        db.delete_table('credits_applicabilityreason')

        # Deleting model 'Unit'
        db.delete_table('credits_unit')

        # Deleting model 'DocumentationField'
        db.delete_table('credits_documentationfield')

        # Removing unique constraint on 'DocumentationField', fields ['credit', 'identifier']
        db.delete_unique('credits_documentationfield', ['credit_id', 'identifier'])

        # Deleting model 'Choice'
        db.delete_table('credits_choice')
    
    
    models = {
        'credits.applicabilityreason': {
            'Meta': {'object_name': 'ApplicabilityReason'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        }
    }
    
    complete_apps = ['credits']
