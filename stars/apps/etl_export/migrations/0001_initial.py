# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'ETL'
        db.create_table('etl_export_etl', (
            ('liaison_department', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('liaison_phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')()),
            ('submission_due_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('participant_status', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('latest_rating', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['credits.Rating'], null=True, blank=True)),
            ('rating_valid_until', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('aashe_id', self.gf('django.db.models.fields.IntegerField')()),
            ('last_submission_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('liaison_title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('current_stars_version', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('liaison_first_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_last_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('liaison_middle_name', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('liaison_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal('etl_export', ['ETL'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'ETL'
        db.delete_table('etl_export_etl')
    
    
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
