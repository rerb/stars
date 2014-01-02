# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):

        mbtu = orm.Unit.objects.get(name='MBtu')
        mmbtu = orm.Unit.objects.get(name='MMBtu')

        mbtu.equivalent = mbtu
        mbtu.ratio = 1
        mbtu.save()

        mmbtu.equivalent = mmbtu
        mmbtu.ratio = 1
        mmbtu.save()

        metric_tons_of_co2_equivalent = orm.Unit.objects.get(
            name='Metric Tons of CO2 Equivalent')
        metric_tons_of_co2_equivalent.equivalent = (
            metric_tons_of_co2_equivalent)
        metric_tons_of_co2_equivalent.ratio = 1
        metric_tons_of_co2_equivalent.save()

        us_canadian = orm.Unit.objects.get(name='US/Canadian $')
        us_canadian.equivalent = us_canadian
        us_canadian.ratio = 1
        us_canadian.save()

        cubic_metres = orm.Unit.objects.get(name='Cubic Metres')
        gross_square_metres = orm.Unit.objects.get(name='Gross Square Metres')
        hectares = orm.Unit.objects.get(name='Hectares')
        square_metres = orm.Unit.objects.get(name='Square Metres')
        metric_tons = orm.Unit.objects.get(name='Metric Tons')
        metric_tons_of_co2_equivalent = orm.Unit.objects.get(
            name='Metric Tons of CO2 Equivalent')

        for metric_unit in [cubic_metres, gross_square_metres,
                            hectares, square_metres, metric_tons,
                            metric_tons_of_co2_equivalent]:
            metric_unit.is_metric = True
            metric_unit.save()

        # acres = orm.Unit.objects.get(name='Acres')
        # gallons = orm.Unit.objects.get(name='Gallons')
        # gross_square_feet = orm.Unit.objects.get(name='Gross Square Feet')
        # square_feet = orm.Unit.objects.get(name='Square Feet')
        # tons = orm.Unit.objects.get(name='Tons')

    def backwards(self, orm):
        raise RuntimeError('Cannot reverse this migration.')

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
    symmetrical = True
