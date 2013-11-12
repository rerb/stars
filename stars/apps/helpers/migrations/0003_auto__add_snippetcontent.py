# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SnippetContent'
        db.create_table('helpers_snippetcontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('helpers', ['SnippetContent'])


    def backwards(self, orm):
        
        # Deleting model 'SnippetContent'
        db.delete_table('helpers_snippetcontent')


    models = {
        'helpers.blockcontent': {
            'Meta': {'object_name': 'BlockContent'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'helpers.helpcontext': {
            'Meta': {'object_name': 'HelpContext'},
            'help_text': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'helpers.snippetcontent': {
            'Meta': {'object_name': 'SnippetContent'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['helpers']
