# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ValueDiscount'
        db.create_table('registration_valuediscount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36)),
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('applicability_filter', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('automatic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=78, blank=True)),
            ('percentage', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('registration', ['ValueDiscount'])


    def backwards(self, orm):
        # Deleting model 'ValueDiscount'
        db.delete_table('registration_valuediscount')


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