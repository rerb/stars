# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'HelpContext.name'
        db.alter_column('helpers_helpcontext', 'name', self.gf('django.db.models.fields.CharField')(max_length=64))

    def backwards(self, orm):

        # Changing field 'HelpContext.name'
        db.alter_column('helpers_helpcontext', 'name', self.gf('django.db.models.fields.CharField')(max_length=32))

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