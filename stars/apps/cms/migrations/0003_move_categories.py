# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.template.defaultfilters import slugify

class Migration(DataMigration):
    
    def forwards(self, orm):
        for c in orm.ArticleCategory.objects.filter(depth=0):
            
            cat = orm.Category(
                                title=c.label,
                                slug=slugify(c.label),
                                ordinal=c.ordinal,
                                content=c.description,
                                )
            cat.save()
            
            for s in orm.ArticleCategory.objects.filter(depth=1, parent_term=c.term_id):
                
                sub = orm.Subcategory(
                                      title=s.label,
                                      slug=slugify(s.label),
                                      ordinal=s.ordinal,
                                      content=s.description,
                                      parent=cat
                                      )
                sub.save()
    
    
    def backwards(self, orm):
        "Write your backwards methods here."
    
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'cms.newarticle': {
            'Meta': {'object_name': 'NewArticle'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articles'", 'null': 'True', 'to': "orm['cms.Subcategory']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cms.subcategory': {
            'Meta': {'object_name': 'Subcategory'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subcategories'", 'to': "orm['cms.Category']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }
    
    complete_apps = ['cms']
