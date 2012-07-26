# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        """
        Create subscriptions for all institutions.
        Migrate their payment data accordingly.
        Only creating the most recent subscription...

        Rated Institutions
        ------------------
         - if their latest rated submission deadline hasn't passed
          - create a current subscription with that end date
         - else
          - create an expired subscription with that end date

        Expired Institutions
        --------------------
        Those institutions who never submitted for a rating
        - create a subscription for their last attempt

        Current Participants
        --------------------
        Those institutions who are still working in the tool
        - create a subscription with their current submission's deadline
        """

        td = datetime.timedelta(days=365)

        need_extension = []


        for i in orm.Institution.objects.order_by('name'):
            print "---------------"
            print "%s:" % i.name
            
            # Get all submissions
            for ss in orm['submissions.SubmissionSet'].objects.filter(institution=i).order_by('date_registered').exclude(is_visible=False):
                print "Submission: %s - %s" % (ss.date_registered, ss.submission_deadline)
                
                subscription_end = ss.submission_deadline

                # rated institutions that still have time in their subscription
                # should get a new submission

                # Rated institutions
                ratings_used = 0
                if ss.status == 'r':
                    ratings_used = 1
                    print "Rated: %s" % ss.date_submitted
                    if subscription_end > datetime.date.today():
                        print "****NEEDS EXTENSION****"
                        need_extension.append(ss)
#                        print "creating submissionset and making it active"
##                        ssKlass = orm['submissions.SubmissionSet']
##                        new_ss = ssKlass(
##                                         institution=i,
##                                         date_registered=ss.date_submitted,
##                                         submission_deadline=ss.submission_deadline,
##                                         creditset=ss.creditset,
##                                         registering_user=ss.registering_user,
##                                         status='ps'
##                                        )
#                        new_ss = migrate_ss_version(ss, ss.creditset)
#                        i.current_submission = new_ss
#                        i.save()

                # Create subscriptions and payments for all submissions
                amount_due = 0
                paid_in_full = True
                
                 # if there aren't any payments
                if orm['submissions.Payment'].objects.filter(submissionset=ss).exclude(type='later').count() == 0:
                    for p in orm['submissions.Payment'].objects.filter(submissionset=ss).filter(type='later'):
                        if p.type == 'later':
                            amount_due += p.amount
                    paid_in_full = False

                new_sub = orm.Subscription(
                    institution=i,
                    start_date=ss.date_registered,
                    end_date=ss.submission_deadline,
                    ratings_used=ratings_used,
                    amount_due=amount_due,
                    paid_in_full=paid_in_full
                    )
                new_sub.save()
                print "Created Subscription: %s - %s" % (new_sub.start_date, new_sub.end_date)

                for p in orm['submissions.Payment'].objects.filter(submissionset=ss).exclude(type='later'):
                    new_payment = orm.SubscriptionPayment(
                        subscription=new_sub,
                        date=p.date,
                        amount=p.amount,
                        user=p.user,
                        reason=p.reason,
                        method=p.type,
                        confirmation=p.confirmation
                        )
                    new_payment.save()
                    print "Created Payment: %s (%s)" % (new_payment.amount, new_payment.method)

        print "Need Extension:"
        print "****THESE NEED TO BE DONE MANUALLY UNFORTUNATELY*****"
        for ss in need_extension:
            print ss.institution.name

    def backwards(self, orm):
        "Write your backwards methods here."


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
        'credits.applicabilityreason': {
            'Meta': {'ordering': "('ordinal',)", 'object_name': 'ApplicabilityReason'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.ApplicabilityReason']"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'credits.category': {
            'Meta': {'ordering': "('ordinal',)", 'object_name': 'Category'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'creditset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.CreditSet']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Category']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'credits.choice': {
            'Meta': {'ordering': "('ordinal',)", 'object_name': 'Choice'},
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_bonafide': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Choice']"})
        },
        'credits.credit': {
            'Meta': {'ordering': "('ordinal',)", 'object_name': 'Credit'},
            'applicability': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'criteria': ('django.db.models.fields.TextField', [], {}),
            'formula': ('django.db.models.fields.TextField', [], {'default': "'points = 0'", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'default': "'ID?'", 'max_length': '16'}),
            'measurement': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'point_value': ('django.db.models.fields.FloatField', [], {}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Credit']"}),
            'scoring': ('django.db.models.fields.TextField', [], {}),
            'staff_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Subcategory']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'validation_rules': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
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
        'credits.documentationfield': {
            'Meta': {'ordering': "('ordinal',)", 'unique_together': "(('credit', 'identifier'),)", 'object_name': 'DocumentationField'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'inline_help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_choice_is_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.DocumentationField']"}),
            'required': ('django.db.models.fields.CharField', [], {'default': "'req'", 'max_length': '8'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tooltip_help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'units': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Unit']", 'null': 'True', 'blank': 'True'})
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
        'credits.subcategory': {
            'Meta': {'ordering': "('category', 'ordinal')", 'object_name': 'Subcategory'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'previous_version': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'_next_version'", 'unique': 'True', 'null': 'True', 'to': "orm['credits.Subcategory']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'credits.unit': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Unit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
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
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'executive_contact_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'executive_contact_city': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'executive_contact_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'executive_contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'executive_contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'executive_contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'executive_contact_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'executive_contact_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'executive_contact_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'executive_contact_zip': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'fte': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'international': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_member': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_pcc_signatory': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_pilot_participant': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'org_type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
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
        'submissions.booleansubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'BooleanSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'booleansubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.boundary': {
            'Meta': {'object_name': 'Boundary'},
            'ag_school_details': ('django.db.models.fields.TextField', [], {}),
            'ag_school_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ag_school_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'agr_exp_details': ('django.db.models.fields.TextField', [], {}),
            'agr_exp_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'agr_exp_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'climate_region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.ClimateZone']"}),
            'cultivated_grounds_acres': ('django.db.models.fields.FloatField', [], {}),
            'endowment_size': ('django.db.models.fields.IntegerField', [], {}),
            'farm_details': ('django.db.models.fields.TextField', [], {}),
            'farm_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'farm_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fte_employmees': ('django.db.models.fields.IntegerField', [], {}),
            'fte_students': ('django.db.models.fields.IntegerField', [], {}),
            'graduate_count': ('django.db.models.fields.IntegerField', [], {}),
            'gsf_building_space': ('django.db.models.fields.FloatField', [], {}),
            'gsf_lab_space': ('django.db.models.fields.FloatField', [], {}),
            'hospital_details': ('django.db.models.fields.TextField', [], {}),
            'hospital_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hospital_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'institutional_control': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'med_school_details': ('django.db.models.fields.TextField', [], {}),
            'med_school_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'med_school_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pharm_school_details': ('django.db.models.fields.TextField', [], {}),
            'pharm_school_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pharm_school_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_health_school_details': ('django.db.models.fields.TextField', [], {}),
            'pub_health_school_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_health_school_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sat_campus_details': ('django.db.models.fields.TextField', [], {}),
            'sat_campus_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sat_campus_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_ftc_percent': ('django.db.models.fields.FloatField', [], {}),
            'student_online_percent': ('django.db.models.fields.FloatField', [], {}),
            'student_ptc_percent': ('django.db.models.fields.FloatField', [], {}),
            'student_residential_percent': ('django.db.models.fields.FloatField', [], {}),
            'submissionset': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.SubmissionSet']", 'unique': 'True'}),
            'undergrad_count': ('django.db.models.fields.IntegerField', [], {}),
            'undeveloped_land_acres': ('django.db.models.fields.FloatField', [], {}),
            'vet_school_details': ('django.db.models.fields.TextField', [], {}),
            'vet_school_included': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'vet_school_present': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'submissions.categorysubmission': {
            'Meta': {'ordering': "('category__ordinal',)", 'unique_together': "(('submissionset', 'category'),)", 'object_name': 'CategorySubmission'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionSet']"})
        },
        'submissions.choicesubmission': {
            'Meta': {'object_name': 'ChoiceSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'choicesubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Choice']", 'null': 'True', 'blank': 'True'})
        },
        'submissions.creditsubmission': {
            'Meta': {'ordering': "('credit__type', 'credit__ordinal')", 'object_name': 'CreditSubmission'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'submissions.creditsubmissioninquiry': {
            'Meta': {'object_name': 'CreditSubmissionInquiry'},
            'credit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Credit']"}),
            'explanation': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission_inquiry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionInquiry']"})
        },
        'submissions.credittestsubmission': {
            'Meta': {'ordering': "('credit__type', 'credit__ordinal')", 'object_name': 'CreditTestSubmission', '_ormbases': ['submissions.CreditSubmission']},
            'creditsubmission_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.CreditSubmission']", 'unique': 'True', 'primary_key': 'True'}),
            'expected_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.creditusersubmission': {
            'Meta': {'ordering': "('credit__type', 'credit__ordinal')", 'object_name': 'CreditUserSubmission', '_ormbases': ['submissions.CreditSubmission']},
            'applicability_reason': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.ApplicabilityReason']", 'null': 'True', 'blank': 'True'}),
            'assessed_points': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'creditsubmission_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['submissions.CreditSubmission']", 'unique': 'True', 'primary_key': 'True'}),
            'internal_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'responsible_party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.ResponsibleParty']", 'null': 'True', 'blank': 'True'}),
            'responsible_party_confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subcategory_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubcategorySubmission']"}),
            'submission_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'submission_status': ('django.db.models.fields.CharField', [], {'default': "'ns'", 'max_length': '8'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'submissions.datacorrectionrequest': {
            'Meta': {'object_name': 'DataCorrectionRequest'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'explanation': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_value': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'submissions.datesubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'DateSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datesubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.extensionrequest': {
            'Meta': {'object_name': 'ExtensionRequest'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_deadline': ('django.db.models.fields.DateField', [], {}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionSet']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'submissions.longtextsubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'LongTextSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'longtextsubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.multichoicesubmission': {
            'Meta': {'object_name': 'MultiChoiceSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'multichoicesubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['credits.Choice']", 'null': 'True', 'blank': 'True'})
        },
        'submissions.numericsubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'NumericSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'numericsubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'submissions.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': "'16'", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': "'16'"}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionSet']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': "'8'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'submissions.reportingfielddatacorrection': {
            'Meta': {'object_name': 'ReportingFieldDataCorrection'},
            'change_date': ('django.db.models.fields.DateField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'explanation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'previous_value': ('django.db.models.fields.TextField', [], {}),
            'request': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'applied_correction'", 'unique': 'True', 'null': 'True', 'to': "orm['submissions.DataCorrectionRequest']"})
        },
        'submissions.responsibleparty': {
            'Meta': {'ordering': "('last_name', 'first_name')", 'object_name': 'ResponsibleParty'},
            'department': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['institutions.Institution']"}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'submissions.subcategorysubmission': {
            'Meta': {'ordering': "('subcategory__ordinal',)", 'unique_together': "(('category_submission', 'subcategory'),)", 'object_name': 'SubcategorySubmission'},
            'category_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CategorySubmission']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['credits.Subcategory']"})
        },
        'submissions.submissioninquiry': {
            'Meta': {'object_name': 'SubmissionInquiry'},
            'additional_comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.SubmissionSet']"})
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
            'submission_deadline': ('django.db.models.fields.DateField', [], {}),
            'submitting_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submitted_submissions'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'submissions.textsubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'TextSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'textsubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'submissions.uploadsubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'UploadSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'uploadsubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'submissions.urlsubmission': {
            'Meta': {'unique_together': "(('documentation_field', 'credit_submission'),)", 'object_name': 'URLSubmission'},
            'credit_submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['submissions.CreditSubmission']"}),
            'documentation_field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'urlsubmission_set'", 'to': "orm['credits.DocumentationField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['submissions', 'institutions']
