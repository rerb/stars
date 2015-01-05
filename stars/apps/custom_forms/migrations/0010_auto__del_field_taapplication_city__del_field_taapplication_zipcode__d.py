# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'TAApplication.city'
        db.delete_column('custom_forms_taapplication', 'city')

        # Deleting field 'TAApplication.zipcode'
        db.delete_column('custom_forms_taapplication', 'zipcode')

        # Deleting field 'TAApplication.state'
        db.delete_column('custom_forms_taapplication', 'state')

        # Deleting field 'TAApplication.address'
        db.delete_column('custom_forms_taapplication', 'address')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'TAApplication.city'
        raise RuntimeError("Cannot reverse this migration. 'TAApplication.city' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'TAApplication.zipcode'
        raise RuntimeError("Cannot reverse this migration. 'TAApplication.zipcode' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'TAApplication.state'
        raise RuntimeError("Cannot reverse this migration. 'TAApplication.state' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'TAApplication.address'
        raise RuntimeError("Cannot reverse this migration. 'TAApplication.address' and its values cannot be restored.")

    models = {
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
        'custom_forms.datadisplayaccessrequest': {
            'Meta': {'object_name': 'DataDisplayAccessRequest'},
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'audience': ('django.db.models.fields.TextField', [], {}),
            'city_state': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'has_instructor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'how_data_used': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'period': ('django.db.models.fields.DateField', [], {}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'will_publish': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'custom_forms.eligibilityquery': {
            'Meta': {'object_name': 'EligibilityQuery'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'included_in_boundary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'other_affiliates': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rationale': ('django.db.models.fields.TextField', [], {}),
            'requesting_institution': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'separate_administration': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'custom_forms.steeringcommitteenomination': {
            'Meta': {'object_name': 'SteeringCommitteeNomination'},
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'perspectives': ('django.db.models.fields.TextField', [], {}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'resume': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'skills': ('django.db.models.fields.TextField', [], {}),
            'strengths': ('django.db.models.fields.TextField', [], {}),
            'successful': ('django.db.models.fields.TextField', [], {}),
            'why': ('django.db.models.fields.TextField', [], {})
        },
        'custom_forms.taapplication': {
            'Meta': {'object_name': 'TAApplication'},
            'credit_weakness': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_registered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instituion_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'related_associations': ('django.db.models.fields.TextField', [], {}),
            'resume': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'skills_and_experience': ('django.db.models.fields.TextField', [], {}),
            'subcategories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['credits.Subcategory']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['custom_forms']