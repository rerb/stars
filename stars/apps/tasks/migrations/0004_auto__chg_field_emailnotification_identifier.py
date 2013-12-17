# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'EmailNotification.identifier'
        db.alter_column('tasks_emailnotification', 'identifier', self.gf('django.db.models.fields.CharField')(max_length=16))

    def backwards(self, orm):

        # Changing field 'EmailNotification.identifier'
        db.alter_column('tasks_emailnotification', 'identifier', self.gf('django.db.models.fields.CharField')(max_length=8))

    models = {
        'tasks.emailnotification': {
            'Meta': {'object_name': 'EmailNotification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'notification_type': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sent_to': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['tasks']