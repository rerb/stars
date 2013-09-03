# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'EmailNotification'
        db.create_table('tasks_emailnotification', (
            ('sent_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('sent_to', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('notification_type', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('tasks', ['EmailNotification'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'EmailNotification'
        db.delete_table('tasks_emailnotification')
    
    
    models = {
        'tasks.emailnotification': {
            'Meta': {'object_name': 'EmailNotification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'notification_type': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sent_to': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }
    
    complete_apps = ['tasks']
