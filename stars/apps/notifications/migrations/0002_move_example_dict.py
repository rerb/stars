# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        db.rename_column('notifications_emailtemplate', 'example_context', 'example_data')


    def backwards(self, orm):
        db.rename_column('notifications_emailtemplate', 'example_data', 'example_context')


    models = {
        'notifications.emailtemplate': {
            'Meta': {'ordering': "('slug',)", 'object_name': 'EmailTemplate'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'example_data': ('jsonfield.fields.JSONField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['notifications']
