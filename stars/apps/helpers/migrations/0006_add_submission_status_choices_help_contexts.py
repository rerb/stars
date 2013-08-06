# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        help_context = orm.HelpContext(
            name='submission-status-choice-in-progress',
            title='In Progress',
            help_text=('You are still editing a credit. Before completing '
                       'the final submission, you will be prompted to '
                       'review any credits marked as “In Progress.”'))
        help_context.save()

        help_context = orm.HelpContext(
            name='submission-status-choice-pursuing',
            title='Pursuing',
            help_text=('All of the required fields have been completed. '
                       'After indicating that a credit is “Complete,” you '
                       'WILL be able to return and edit the information '
                       'entered for the credit before making the entire '
                       'submission final.'))
        help_context.save()

        help_context = orm.HelpContext(
            name='submission-status-choice-not-applicable',
            title='Not Applicable',
            help_text=('An institution could not possibly earn the credit '
                       'due to institutional circumstances. For example, '
                       'credits about residence halls do not apply to '
                       'institutions that do not have residence halls. '
                       'An institution’s overall score is based on the '
                       'percentage of applicable points it earns. In other '
                       'words, credits that do not apply to an institution '
                       'will not be counted against that institution\’s '
                       'overall score.'))
        help_context.save()

        help_context = orm.HelpContext(
            name='submission-status-choice-not-pursuing',
            title='Not Pursuing',
            help_text=('You do not wish to submit data for a credit. When '
                       'the final submission is made public, only the '
                       '“Public Notes” field for credits with this status '
                       'will be made public. Institutions will not earn '
                       'points for credits marked as “Not Pursuing.”'))
        help_context.save()

    def backwards(self, orm):
        "Write your backwards methods here."

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
    symmetrical = True
