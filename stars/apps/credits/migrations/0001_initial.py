# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IncrementalFeature'
        db.create_table('credits_incrementalfeature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('credits', ['IncrementalFeature'])

        # Adding model 'CreditSet'
        db.create_table('credits_creditset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('previous_version', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='_next_version', unique=True, null=True, to=orm['credits.CreditSet'])),
            ('version', self.gf('django.db.models.fields.CharField')(unique=True, max_length=5)),
            ('release_date', self.gf('django.db.models.fields.DateField')()),
            ('tier_2_points', self.gf('django.db.models.fields.FloatField')()),
            ('is_locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('scoring_method', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('credit_identifier', self.gf('django.db.models.fields.CharField')(default='get_1_1_identifier', max_length=25)),
        ))
        db.send_create_signal('credits', ['CreditSet'])

        # Adding M2M table for field supported_features on 'CreditSet'
        m2m_table_name = db.shorten_name('credits_creditset_supported_features')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('creditset', models.ForeignKey(orm['credits.creditset'], null=False)),
            ('incrementalfeature', models.ForeignKey(orm['credits.incrementalfeature'], null=False))
        ))
        db.create_unique(m2m_table_name, ['creditset_id', 'incrementalfeature_id'])

        # Adding model 'Rating'
        db.create_table('credits_rating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='16')),
            ('minimal_score', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('creditset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.CreditSet'])),
            ('image_200', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('image_large', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('map_icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('publish_score', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('credits', ['Rating'])

        # Adding model 'Category'
        db.create_table('credits_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('previous_version', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='_next_version', unique=True, null=True, to=orm['credits.Category'])),
            ('creditset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.CreditSet'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('max_point_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('include_in_report', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('include_in_score', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('credits', ['Category'])

        # Adding model 'Subcategory'
        db.create_table('credits_subcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('previous_version', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='_next_version', unique=True, null=True, to=orm['credits.Subcategory'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Category'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=64, null=True, blank=True)),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('max_point_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('passthrough', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('credits', ['Subcategory'])

        # Adding model 'Credit'
        db.create_table('credits_credit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('previous_version', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='_next_version', unique=True, null=True, to=orm['credits.Credit'])),
            ('subcategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Subcategory'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('number', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('point_value', self.gf('django.db.models.fields.FloatField')()),
            ('point_minimum', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('point_variation_reason', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('point_value_formula', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('formula', self.gf('django.db.models.fields.TextField')(default='points = 0', null=True, blank=True)),
            ('validation_rules', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('criteria', self.gf('django.db.models.fields.TextField')()),
            ('applicability', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('scoring', self.gf('django.db.models.fields.TextField')()),
            ('measurement', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('staff_notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(default='ID?', max_length=16)),
            ('show_info', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requires_responsible_party', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('resources', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('credits', ['Credit'])

        # Adding model 'ApplicabilityReason'
        db.create_table('credits_applicabilityreason', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('previous_version', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='_next_version', unique=True, null=True, to=orm['credits.ApplicabilityReason'])),
            ('credit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Credit'])),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('help_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ordinal', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('credits', ['ApplicabilityReason'])

        # Adding model 'Unit'
        db.create_table('credits_unit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('equivalent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Unit'], null=True, blank=True)),
            ('ratio', self.gf('django.db.models.fields.FloatField')(default=1.0, null=True, blank=True)),
            ('is_metric', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('credits', ['Unit'])

        # Adding model 'DocumentationField'
        db.create_table('credits_documentationfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('previous_version', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='_next_version', unique=True, null=True, to=orm['credits.DocumentationField'])),
            ('credit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Credit'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('last_choice_is_other', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('min_range', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max_range', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('units', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Unit'], null=True, blank=True)),
            ('inline_help_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('tooltip_help_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('required', self.gf('django.db.models.fields.CharField')(default='req', max_length=8)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tabular_fields', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('credits', ['DocumentationField'])

        # Adding unique constraint on 'DocumentationField', fields ['credit', 'identifier']
        db.create_unique('credits_documentationfield', ['credit_id', 'identifier'])

        # Adding model 'Choice'
        db.create_table('credits_choice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('previous_version', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='_next_version', unique=True, null=True, to=orm['credits.Choice'])),
            ('documentation_field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.DocumentationField'])),
            ('choice', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('is_bonafide', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('credits', ['Choice'])


    def backwards(self, orm):
        # Removing unique constraint on 'DocumentationField', fields ['credit', 'identifier']
        db.delete_unique('credits_documentationfield', ['credit_id', 'identifier'])

        # Deleting model 'IncrementalFeature'
        db.delete_table('credits_incrementalfeature')

        # Deleting model 'CreditSet'
        db.delete_table('credits_creditset')

        # Removing M2M table for field supported_features on 'CreditSet'
        db.delete_table(db.shorten_name('credits_creditset_supported_features'))

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

        # Deleting model 'Choice'
        db.delete_table('credits_choice')


    models = {
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
            'identifier': ('django.db.models.fields.CharField', [], {'default': "'ID?'", 'max_length': '16'}),
            'is_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'measurement': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'point_minimum': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'point_value': ('django.db.models.fields.FloatField', [], {}),
            'point_value_formula': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'point_variation_reason': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Credit']"}),
            'requires_responsible_party': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'resources': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'scoring': ('django.db.models.fields.TextField', [], {}),
            'show_info': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'staff_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Subcategory']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
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
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'inline_help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_choice_is_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.DocumentationField']"}),
            'required': ('django.db.models.fields.CharField', [], {'default': "'req'", 'max_length': '8'}),
            'tabular_fields': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tooltip_help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
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
        }
    }

    complete_apps = ['credits']