# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'BlockContent.key'
        db.alter_column('helpers_blockcontent', 'key', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50))

        # Adding index on 'BlockContent', fields ['key']
        db.create_index('helpers_blockcontent', ['key'])
    
    
    def backwards(self, orm):
        
        # Changing field 'BlockContent.key'
        db.alter_column('helpers_blockcontent', 'key', self.gf('django.db.models.fields.CharField')(max_length=16, unique=True))

        # Removing index on 'BlockContent', fields ['key']
        db.delete_index('helpers_blockcontent', ['key'])
    
    
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
        }
    }
    
    complete_apps = ['helpers']
