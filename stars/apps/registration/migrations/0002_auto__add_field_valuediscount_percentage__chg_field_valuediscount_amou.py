# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ValueDiscount.percentage'
        db.add_column('registration_valuediscount', 'percentage',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


        # Changing field 'ValueDiscount.amount'
        db.alter_column('registration_valuediscount', 'amount', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'ValueDiscount.code'
        db.alter_column('registration_valuediscount', 'code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36))
        # Adding unique constraint on 'ValueDiscount', fields ['code']
        db.create_unique('registration_valuediscount', ['code'])


    def backwards(self, orm):
        # Removing unique constraint on 'ValueDiscount', fields ['code']
        db.delete_unique('registration_valuediscount', ['code'])

        # Deleting field 'ValueDiscount.percentage'
        db.delete_column('registration_valuediscount', 'percentage')


        # Changing field 'ValueDiscount.amount'
        db.alter_column('registration_valuediscount', 'amount', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'ValueDiscount.code'
        db.alter_column('registration_valuediscount', 'code', self.gf('django.db.models.fields.CharField')(max_length=16))

    models = {
        'registration.valuediscount': {
            'Meta': {'object_name': 'ValueDiscount'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percentage': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['registration']