# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    
    def forwards(self, orm):
        "Pull the rating from the foreign key relationship and add the string version to current_rating"
        
        for etl in orm.ETL.objects.all():
            if etl.latest_rating:
                etl.current_rating = etl.latest_rating.name
                etl.save()
    
    def backwards(self, orm):
        "Undo this migration by pulling the foreign keys back using the name of the rating"
        
        for etl in orm.ETL.objects.all():
            if etl.current_rating:
                etl.latest_rating = orm['credits.Rating'].objects.get(name=etl.current_rating)
                etl.save()
    
    models = {
        'credits.creditset': {
            'Meta': {'object_name': 'CreditSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'release_date': ('django.db.models.fields.DateField', [], {}),
            'scoring_method': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'tier_2_points': ('django.db.models.fields.FloatField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'})
        },
        'credits.rating': {
            'Meta': {'object_name': 'Rating'},
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimal_score': ('django.db.models.fields.SmallIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'16'"})
        },
        'etl_export.etl': {
            'Meta': {'object_name': 'ETL'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'current_rating': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'current_stars_version': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_submission_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'latest_rating': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Rating']", 'null': 'True', 'blank': 'True'}),
            'liaison_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'liaison_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'liaison_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'liaison_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'liaison_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'liaison_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {}),
            'liaison_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'participant_status': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'rating_valid_until': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'submission_due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['etl_export']
