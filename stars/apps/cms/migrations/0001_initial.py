# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'ArticleCategory'
        db.create_table('cms_articlecategory', (
            ('ordinal', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('term_id', self.gf('django.db.models.fields.IntegerField')(unique=True, primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('depth', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('parent_term', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('cms', ['ArticleCategory'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'ArticleCategory'
        db.delete_table('cms_articlecategory')
    
    
    models = {
        'cms.articlecategory': {
            'Meta': {'object_name': 'ArticleCategory'},
            'depth': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent_term': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'term_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'})
        }
    }
    
    complete_apps = ['cms']
