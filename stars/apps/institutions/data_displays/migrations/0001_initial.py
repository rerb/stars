# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AuthorizedUser'
        db.create_table('data_displays_authorizeduser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('member_level', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('participant_level', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('data_displays', ['AuthorizedUser'])


    def backwards(self, orm):
        
        # Deleting model 'AuthorizedUser'
        db.delete_table('data_displays_authorizeduser')


    models = {
        'data_displays.authorizeduser': {
            'Meta': {'ordering': "('-start_date', '-end_date')", 'object_name': 'AuthorizedUser'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member_level': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'participant_level': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['data_displays']
