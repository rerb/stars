# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('old_cms_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('old_cms', ['Category'])

        # Adding model 'Subcategory'
        db.create_table('old_cms_subcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['old_cms.Category'])),
        ))
        db.send_create_signal('old_cms', ['Subcategory'])

        # Adding model 'NewArticle'
        db.create_table('old_cms_newarticle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('teaser', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('irc_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('old_cms', ['NewArticle'])

        # Adding M2M table for field categories on 'NewArticle'
        m2m_table_name = db.shorten_name('old_cms_newarticle_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newarticle', models.ForeignKey(orm['old_cms.newarticle'], null=False)),
            ('category', models.ForeignKey(orm['old_cms.category'], null=False))
        ))
        db.create_unique(m2m_table_name, ['newarticle_id', 'category_id'])

        # Adding model 'HomepageUpdate'
        db.create_table('old_cms_homepageupdate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ordinal', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('old_cms', ['HomepageUpdate'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('old_cms_category')

        # Deleting model 'Subcategory'
        db.delete_table('old_cms_subcategory')

        # Deleting model 'NewArticle'
        db.delete_table('old_cms_newarticle')

        # Removing M2M table for field categories on 'NewArticle'
        db.delete_table(db.shorten_name('old_cms_newarticle_categories'))

        # Deleting model 'HomepageUpdate'
        db.delete_table('old_cms_homepageupdate')


    models = {
        'old_cms.category': {
            'Meta': {'object_name': 'Category'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'old_cms.homepageupdate': {
            'Meta': {'ordering': "('ordinal', 'title', 'timestamp')", 'object_name': 'HomepageUpdate'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'old_cms.newarticle': {
            'Meta': {'ordering': "('ordinal', 'title', 'timestamp')", 'object_name': 'NewArticle'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['old_cms.Category']", 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'irc_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'teaser': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'old_cms.subcategory': {
            'Meta': {'object_name': 'Subcategory'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['old_cms.Category']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['old_cms']