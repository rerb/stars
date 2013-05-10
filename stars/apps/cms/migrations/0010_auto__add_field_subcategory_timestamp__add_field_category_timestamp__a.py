# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'Subcategory.timestamp'
        db.add_column('cms_subcategory', 'timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2010, 12, 8, 21, 1, 30, 29654), blank=True), keep_default=False)

        # Adding field 'Category.timestamp'
        db.add_column('cms_category', 'timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2010, 12, 8, 21, 1, 47, 406040), blank=True), keep_default=False)

        # Adding field 'NewArticle.timestamp'
        db.add_column('cms_newarticle', 'timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2010, 12, 8, 21, 1, 50, 622406), blank=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting field 'Subcategory.timestamp'
        db.delete_column('cms_subcategory', 'timestamp')

        # Deleting field 'Category.timestamp'
        db.delete_column('cms_category', 'timestamp')

        # Deleting field 'NewArticle.timestamp'
        db.delete_column('cms_newarticle', 'timestamp')
    
    
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
        },
        'cms.category': {
            'Meta': {'object_name': 'Category'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'cms.newarticle': {
            'Meta': {'object_name': 'NewArticle'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['cms.Category']", 'null': 'True', 'blank': 'True'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'irc_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'subcategories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['cms.Subcategory']", 'null': 'True', 'blank': 'True'}),
            'teaser': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cms.subcategory': {
            'Meta': {'object_name': 'Subcategory'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Category']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }
    
    complete_apps = ['cms']
