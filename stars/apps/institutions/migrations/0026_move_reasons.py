# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """
            Move reasons from Payments over to Subscriptions
        """
        for sub in orm.Subscription.objects.all():
#            print "-------------"
#            print sub.institution
#            print "%s - %s" % (sub.start_date, sub.end_date)
#            print "other subscriptions"
#            for s in sub.institution.subscription_set.all():
#                if s.id != sub.id:
#                    print "%s - %s" % (s.start_date, s.end_date)
            
            # if there are previous subscriptions, then this is a renewal
            if sub.institution.subscription_set.filter(start_date__lt=sub.start_date).count() > 0:
                if sub.institution.is_member:
                    sub.reason = "member_renew"
                else:
                    sub.reason = "nonmember_renew"
            else:
                if sub.institution.is_member:
                    sub.reason = "member_reg"
                else:
                    sub.reason = "nonmember_reg"
            sub.save()
#            print "logic: %s" % sub.reason

    def backwards(self, orm):
        "Write your backwards methods here."
        pass

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'credits.creditset': {
            'Meta': {'ordering': "('release_date',)", 'object_name': 'CreditSet'},
            'credit_identifier': ('django.db.models.fields.CharField', [], {'default': "'get_1_0_identifier'", 'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.CreditSet']"}),
            'release_date': ('django.db.models.fields.DateField', [], {}),
            'scoring_method': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'supported_features': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['credits.IncrementalFeature']", 'symmetrical': 'False'}),
            'tier_2_points': ('django.db.models.fields.FloatField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'})
        },
        'credits.incrementalfeature': {
            'Meta': {'object_name': 'IncrementalFeature'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'credits.rating': {
            'Meta': {'ordering': "('-minimal_score',)", 'object_name': 'Rating'},
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_200': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_large': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'map_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'minimal_score': ('django.db.models.fields.SmallIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'16'"}),
            'publish_score': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'institutions.accountinvite': {
            'Meta': {'object_name': 'AccountInvite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'institutions.baseaccount': {
            'Meta': {'object_name': 'BaseAccount'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'institutions.climatezone': {
            'Meta': {'object_name': 'ClimateZone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'institutions.institution': {
            'Meta': {'object_name': 'Institution'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'charter_participant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'contact_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'contact_phone_ext': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'contact_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'current_rating': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Rating']", 'null': 'True', 'blank': 'True'}),
            'current_submission': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current'", 'null': 'True', 'to': "orm['submissions.SubmissionSet']"}),
            'current_subscription': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current'", 'null': 'True', 'to': "orm['institutions.Subscription']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'executive_contact_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'executive_contact_city': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'executive_contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'executive_contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'executive_contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'executive_contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'executive_contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'executive_contact_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'executive_contact_title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'executive_contact_zip': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'fte': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'international': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_member': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_participant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_pcc_signatory': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_pilot_participant': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'org_type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'president_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'president_city': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'president_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'president_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'president_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'president_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'president_title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'president_zip': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'rated_submission': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rated'", 'null': 'True', 'to': "orm['submissions.SubmissionSet']"}),
            'rating_expires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'stars_staff_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'institutions.institutionpreferences': {
            'Meta': {'object_name': 'InstitutionPreferences'},
            'institution': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'preferences'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['institutions.Institution']"}),
            'notify_users': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'institutions.institutionstate': {
            'Meta': {'object_name': 'InstitutionState'},
            'active_submission_set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'active_submission'", 'to': "orm['submissions.SubmissionSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'state'", 'unique': 'True', 'to': "orm['institutions.Institution']"}),
            'latest_rated_submission_set': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'rated_submission'", 'null': 'True', 'blank': 'True', 'to': "orm['submissions.SubmissionSet']"})
        },
        'institutions.pendingaccount': {
            'Meta': {'unique_together': "(('user_email', 'institution'),)", 'object_name': 'PendingAccount'},
            'baseaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['institutions.BaseAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'terms_of_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'user_level': ('django.db.models.fields.CharField', [], {'max_length': "'6'"})
        },
        'institutions.registrationreason': {
            'Meta': {'object_name': 'RegistrationReason'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'institutions.registrationsurvey': {
            'Meta': {'object_name': 'RegistrationSurvey'},
            'enhancements': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'other': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'primary_reason': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'primary_surveys'", 'null': 'True', 'to': "orm['institutions.RegistrationReason']"}),
            'reasons': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['institutions.RegistrationReason']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'institutions.respondentregistrationreason': {
            'Meta': {'object_name': 'RespondentRegistrationReason'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'institutions.respondentsurvey': {
            'Meta': {'object_name': 'RespondentSurvey'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'other': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'potential_stars': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'reasons': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['institutions.RespondentRegistrationReason']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'institutions.starsaccount': {
            'Meta': {'unique_together': "(('user', 'institution'),)", 'object_name': 'StarsAccount'},
            'baseaccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['institutions.BaseAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'is_selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'terms_of_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'user_level': ('django.db.models.fields.CharField', [], {'max_length': "'6'"})
        },
        'institutions.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'amount_due': ('django.db.models.fields.FloatField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'paid_in_full': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ratings_allocated': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'ratings_used': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'institutions.subscriptionpayment': {
            'Meta': {'object_name': 'SubscriptionPayment'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': "'8'"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'16'"}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Subscription']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'submissions.submissionset': {
            'Meta': {'ordering': "('date_registered',)", 'object_name': 'SubmissionSet'},
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'date_registered': ('django.db.models.fields.DateField', [], {}),
            'date_reviewed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_submitted': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'pdf_report': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'presidents_letter': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Rating']", 'null': 'True', 'blank': 'True'}),
            'registering_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'registered_submissions'", 'to': "orm['auth.User']"}),
            'reporter_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'submission_boundary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'submitting_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submitted_submissions'", 'null': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['institutions']
