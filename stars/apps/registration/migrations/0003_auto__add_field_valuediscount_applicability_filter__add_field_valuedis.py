# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ValueDiscount.applicability_filter'
        db.add_column('registration_valuediscount', 'applicability_filter',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'ValueDiscount.automatic'
        db.add_column('registration_valuediscount', 'automatic',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ValueDiscount.description'
        db.add_column('registration_valuediscount', 'description',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=78, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ValueDiscount.applicability_filter'
        db.delete_column('registration_valuediscount', 'applicability_filter')

        # Deleting field 'ValueDiscount.automatic'
        db.delete_column('registration_valuediscount', 'automatic')

        # Deleting field 'ValueDiscount.description'
        db.delete_column('registration_valuediscount', 'description')


    models = {
        'registration.valuediscount': {
            'Meta': {'object_name': 'ValueDiscount'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'applicability_filter': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'automatic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '78', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percentage': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['registration']