# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Subcategory'
        db.create_table('cms_subcategory', (
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subcategories', to=orm['cms.Category'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('cms', ['Subcategory'])

        # Adding model 'Category'
        db.create_table('cms_category', (
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('cms', ['Category'])

        # Adding model 'NewArticle'
        db.create_table('cms_newarticle', (
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('stamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('cms', ['NewArticle'])

        # Adding M2M table for field subcategories on 'NewArticle'
        db.create_table('cms_newarticle_subcategories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newarticle', models.ForeignKey(orm['cms.newarticle'], null=False)),
            ('subcategory', models.ForeignKey(orm['cms.subcategory'], null=False))
        ))
        db.create_unique('cms_newarticle_subcategories', ['newarticle_id', 'subcategory_id'])

        # Adding M2M table for field categories on 'NewArticle'
        db.create_table('cms_newarticle_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newarticle', models.ForeignKey(orm['cms.newarticle'], null=False)),
            ('category', models.ForeignKey(orm['cms.category'], null=False))
        ))
        db.create_unique('cms_newarticle_categories', ['newarticle_id', 'category_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Subcategory'
        db.delete_table('cms_subcategory')

        # Deleting model 'Category'
        db.delete_table('cms_category')

        # Deleting model 'NewArticle'
        db.delete_table('cms_newarticle')

        # Removing M2M table for field subcategories on 'NewArticle'
        db.delete_table('cms_newarticle_subcategories')

        # Removing M2M table for field categories on 'NewArticle'
        db.delete_table('cms_newarticle_categories')
    
    
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
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'cms.newarticle': {
            'Meta': {'object_name': 'NewArticle'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['cms.Category']", 'null': 'True', 'blank': 'True'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'subcategories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['cms.Subcategory']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cms.subcategory': {
            'Meta': {'object_name': 'Subcategory'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subcategories'", 'to': "orm['cms.Category']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }
    
    complete_apps = ['cms']
