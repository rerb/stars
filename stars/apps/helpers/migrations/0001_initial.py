# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HelpContext'
        db.create_table('helpers_helpcontext', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('help_text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('helpers', ['HelpContext'])

        # Adding model 'BlockContent'
        db.create_table('helpers_blockcontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('helpers', ['BlockContent'])

        # Adding model 'SnippetContent'
        db.create_table('helpers_snippetcontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('helpers', ['SnippetContent'])


    def backwards(self, orm):
        # Deleting model 'HelpContext'
        db.delete_table('helpers_helpcontext')

        # Deleting model 'BlockContent'
        db.delete_table('helpers_blockcontent')

        # Deleting model 'SnippetContent'
        db.delete_table('helpers_snippetcontent')


    models = {
        'helpers.blockcontent': {
            'Meta': {'object_name': 'BlockContent'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'helpers.helpcontext': {
            'Meta': {'object_name': 'HelpContext'},
            'help_text': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'helpers.snippetcontent': {
            'Meta': {'object_name': 'SnippetContent'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['helpers']