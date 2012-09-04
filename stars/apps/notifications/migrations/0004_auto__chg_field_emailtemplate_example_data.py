# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'EmailTemplate.example_data'
        db.alter_column('notifications_emailtemplate', 'example_data', self.gf('jsonfield.fields.JSONField')(null=True))


    def backwards(self, orm):
        
        # Changing field 'EmailTemplate.example_data'
        db.alter_column('notifications_emailtemplate', 'example_data', self.gf('jsonfield.fields.JSONField')(default={}))


    models = {
        'notifications.copyemail': {
            'Meta': {'object_name': 'CopyEmail'},
            'address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'bcc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['notifications.EmailTemplate']"})
        },
        'notifications.emailtemplate': {
            'Meta': {'ordering': "('slug',)", 'object_name': 'EmailTemplate'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'example_data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['notifications']
