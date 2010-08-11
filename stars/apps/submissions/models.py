from datetime import datetime, date
import os, re
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db.models import Q

from stars.apps.credits.models import *
from stars.apps.institutions.models import Institution
from stars.apps.helpers import watchdog
from stars.apps.helpers import flashMessage
from stars.apps.helpers import managers
            
SUBMISSION_STATUS_CHOICES = (
    ('ps', 'Pending Submission'),
    ('pr', 'Pending Review'),
    ('r', 'Rated'),
)

REGISTRATION_PUBLISH_DEADLINE = date(2010, 5, 29)

def president_letter_callback(instance, filename):
    """
        Dynamically alters the upload path based on the instance
        secure/<org_id>/letter/<file_name>.<ext>
    """
    institution = instance.institution
    path = "secure/%d/letter/%s" % (institution.id, filename)
    return path

class SubmissionManager(models.Manager):
    """
        Adds some custom query functionality to the SubmissionSet object
    """
    
    def published(self):
        """ Submissionsets that have been paid in full or unpaid before May 28th """
        
        deadline = REGISTRATION_PUBLISH_DEADLINE
        qs1 = SubmissionSet.objects.filter(institution__enabled=True).filter(payment__isnull=False)
        qs2 = qs1.filter(
                (Q(payment__type='later') & Q(date_registered__lte=deadline)) | ~Q(payment__type='later'))
        return qs2

class SubmissionSet(models.Model):
    """
        A creditset (ex: 1.0) that is being submitted
    """
    objects = SubmissionManager()
    creditset = models.ForeignKey(CreditSet)
    institution = models.ForeignKey(Institution)
    date_registered = models.DateField()
    date_submitted = models.DateField(blank=True, null=True)
    date_reviewed = models.DateField(blank=True, null=True)
    submission_deadline = models.DateField()
    registering_user = models.ForeignKey(User, related_name='registered_submissions')
    submitting_user = models.ForeignKey(User, related_name='submitted_submissions', blank=True, null=True)
    rating = models.ForeignKey(Rating, blank=True, null=True)
    status = models.CharField(max_length=8, choices=SUBMISSION_STATUS_CHOICES)
    submission_boundary = models.TextField(blank=True, null=True, help_text='Each institution is expected to include its entire main campus when collecting data.  Institutions may choose to include any other land holdings, facilities, farms, and satellite campuses, as long as the selected boundary is the same for each credit.  If an institution finds it necessary to exclude a particular unit from its entire submission or a particular credit, the reason for excluding it must be provided in the notes for that credit or in this description.')
    presidents_letter = models.FileField("President's Letter", upload_to=president_letter_callback, blank=True, null=True, help_text="AASHE requires that every submission be vouched for by that institution's president. Please upload a PDF or scan of a letter from your president.")
    reporter_status = models.BooleanField(help_text="Check this box if you would like to be given reporter status and not receive a STARS rating from AASHE.")
    
    # class Meta:
    #     unique_together = ("institution", "creditset")  # an institution can only register once for a given creditset.

    def __unicode__(self):
        return unicode('%s (%s)' % (self.institution, self.creditset) )
    
    def is_enabled(self):
        for payment in self.payment_set.all():
            if payment.type == 'credit' or payment.type == 'check':
                return True
        return False
    
    def was_submitted(self):
        " Indicates if this set has been submitted for a rating "
        return self.date_submitted != None
        
    def get_crumb_label(self):
        return str(self.institution)
    
    def get_admin_url(self):
        return "%ssubmissionsets/%d/" % (self.institution.get_admin_url(), self.id)
        
    def get_add_payment_url(self):
        return "%sadd-payment/" % self.get_admin_url()

    def get_manage_url(self):
        return "/tool/manage/submissionsets/%d/" % (self.id)
        
    def get_submit_url(self):
        return "/tool/submissions/submit/"
        
    def get_scorecard_url(self):
        return '/institutions/%s/report/%s/'% (self.institution.id, self.id)

    def get_parent(self):
        """ Used for building crumbs """
        return None
        
    def get_status(self):
        """ Returns a status display string showing current status or rating for this submission """
        if self.is_rated():
            return unicode(self.rating)
        return self.get_status_display()

    def get_submission_date(self):
        """ Returns a reasonable submission date for this submission based on its current status """
        return self.date_reviewed if self.is_rated() else \
               self.date_submitted if self.is_pending_review() else \
               self.submission_deadline

    def is_pending_review(self):
        """ Return True iff this submission set has been rated """
        return self.status == 'pr'
    
    def is_rated(self):
        """ Return True iff this submission set has been rated """
        return self.status == 'r'
    
    def get_total_credits(self):
        total = 0
        for cat in self.creditset.category_set.all():
            for sub in cat.subcategory_set.all():
                total += sub.credit_set.count()
        return total
    
    def get_STARS_rating(self):
        """
            Return the STARS rating (potentially provisional) for this submission
            @todo: this is inefficient - need to store or at least cache the STARS score.
        """
        if self.is_rated():
            return unicode(self.rating)
        else:
            return self.creditset.get_rating(self.get_STARS_score())
    
    def get_STARS_score(self):
        """
            Return the total STARS score for this submission
            Relies on the scoring method defined by the CreditSet model.
             - define version-specific scoring methods below, and add to SCORING_METHOD_CHOICES in CreditSet model.
        """
        scoring_method = self.creditset.scoring_method
        if hasattr(self, scoring_method):
            score = getattr(self, scoring_method)
            return score()
        else:
            watchdog.log("Submissions", "No method (%s) defined to score submission %s"%(scoring_method, self.creditset.version), watchdog.ERROR)
            return 0

    def get_STARS_v1_0_score(self):
        score = 0
        non_inno_cats = 0
        innovation_score = 0
        for cat in self.categorysubmission_set.all():
            if cat.category.is_innovation(): 
                innovation_score = cat.get_STARS_v1_0_score()
            else:
                score += cat.get_STARS_v1_0_score()
                non_inno_cats += 1

        score = (score / non_inno_cats) if non_inno_cats>0 else 0   # average score

        score += innovation_score  # plus any innovation points
        
        return score if score <= 100 else 100
        
    def get_claimed_points(self):
        """
            @TODO: Consider changing this to a stored value in the model
            if we do that we'll probably need transactions
        """
        score = 0
        for cat in self.categorysubmission_set.all():
            score += cat.get_claimed_points()
        return score
        
    def get_available_points(self):
        score = 0
        for cat in self.categorysubmission_set.all():
            score += cat.get_available_points()
        return score
    
    def get_adjusted_available_points(self):
        """ Gets only the points for credits that have not been labelled as Not Applicable """
        score = 0
        for cat in self.categorysubmission_set.all():
            score += cat.get_adjusted_available_points()
        return score
        
    def get_finished_credit_count(self):
        """ Get the number of credits that have been marked complete, not pursuing, or not applicable """
        count = 0
        for cat in self.categorysubmission_set.all():
            count += cat.get_finished_credit_count()
        return count

    def get_percent_complete(self):
        """ Return the percentage of credits completed in the entire set: 0 - 100 """
        total_credits = self.get_total_credits()
        if total_credits == 0: return 0
        return int((self.get_finished_credit_count() / float(total_credits)) * 100)

    def get_progress_title(self):
        """ Returns a title for progress on the entire submission set """
        return "Complete" if self.get_percent_complete() == 100 else "Reporting Status"
        
    def get_amount_due(self):
        """ Returns the amount of the total # of "later" payments tied to this submission """
        total = 0.0
        for p in self.payment_set.filter(type='later'):
            total += p.amount
            
        return total


def get_active_submissions(creditset=None, category=None, subcategory=None, credit=None):
    """ Return a queryset for ALL active (started / finished) credit submissions that meet the given criteria.
        Only ZERO or ONE criteria should be specified - more is redundant and this code does not check for consistency.
    """
    submissions = CreditUserSubmission.objects.all()

    if credit:
        submissions = submissions.filter(credit=credit)
    else:
        # This code may result in a nested query. May not be optimized in MySQL - see Performance Considerations at: http://docs.djangoproject.com/en/dev/ref/models/querysets/#in
        credits = []
        if subcategory:
            credits = subcategory.credit_set.all()
        elif category:
            subcategories = Subcategory.objects.filter(category=category)
            credits = Credit.objects.filter(subcategory__in=subcategories)
        elif creditset:
            categories = Category.objects.filter(creditset=creditset)
            subcategories = Subcategory.objects.filter(category__in=categories)
            credits = Credit.objects.filter(subcategory__in=subcategories)

        submissions = submissions.filter(credit__in=credits)

    return submissions.exclude(submission_status='ns')        

def get_complete_submissions(creditset=None, category=None, subcategory=None, credit=None):
    """ See get_active_submission above - except only returns those marked as complete """
    submissions = get_active_submissions(creditset, category, subcategory, credit)
    return submissions.filter(submission_status='c')
    
def get_active_field_submissions(field):
    """ Return a queryset for ALL active (non-empty) submissions for the given documentations field. """
    FieldClass = DocumentationFieldSubmission.get_field_class(field)
    submissions = FieldClass.objects.filter(documentation_field=field).exclude(value=None)
    if FieldClass is TextSubmission or FieldClass is LongTextSubmission:
        submissions = submissions.exclude(value='')
    return submissions        
    

def get_na_submissions(applicability_reason):
    """ Return a queryset for all n/a submissions that cite the given applicability_reason """
    return CreditUserSubmission.objects.filter(applicability_reason=applicability_reason).filter(submission_status='na')         

def get_id(object):
    """ Return a valid identifier for the given sumbssion set object """
    return str(object).strip().lower().replace(" & ", "-").replace(" ", "-")
    
class CategorySubmission(models.Model):
    """
        A Category from a credit set that is being submitted
    """
    submissionset = models.ForeignKey(SubmissionSet)
    category = models.ForeignKey(Category)

    class Meta:
        unique_together = ("submissionset", "category")
        ordering = ("category__ordinal",)
        
    def __unicode__(self):
        return unicode(self.category)
   
    def get_crumb_label(self):
        return str(self)
    
    def get_institution(self):
        return self.submissionset.institution
        
    def get_creditset(self):
        return self.submissionset.creditset
    
    def get_id(self):
        """ Return a valid identifier representing this category """
        return get_id(self)
     
    def get_total_credits(self):
        total = 0
        for sub in self.subcategorysubmission_set.all():
            total = total + sub.get_total_credits()
        return total

    def get_parent(self):
        """ Used for building crumbs """
        return self.submissionset
        
    def get_submit_url(self):
        return self.category.get_submit_url()
        
    def get_scorecard_url(self):
        return '%s%s' % (self.submissionset.get_scorecard_url(), self.category.get_browse_url())

    def get_STARS_score(self):
        """
            Return the STARS score for this category 
            - this is the fractional score for points earned in this category
            Relies on the scoring method defined for each credit set version:
             - define a version-specific method for each credit set below.
        """
        scoring_method = self.submissionset.creditset.scoring_method
        if hasattr(self, scoring_method):
            score = getattr(self, scoring_method)
            return score()
        else:
            watchdog.log("Submissions", "No method (%s) defined to score category submission %s"%(scoring_method, self.submissionset.creditset.version), watchdog.ERROR)
            return 0

    def get_STARS_v1_0_score(self):
        score = self.get_claimed_points()              # raw score - number of points earned in category
        avail = self.get_adjusted_available_points()  # available / applicable points in category        
        #  score for innovation credits is just the raw score
        #  for all others, it is the proportion of points earned.
        if not self.category.is_innovation(): 
            score = ((100.0 * score) / avail) if avail>0 else 0   # percentage of points earned, 0 - 100
        return score

    def get_claimed_points(self):
        score = 0
        for sub in self.subcategorysubmission_set.all():
            score += sub.get_claimed_points()
        return score
        
    def get_available_points(self):
        score = 0
        for sub in self.subcategorysubmission_set.all():
            score += sub.get_available_points()
        return score
    
    def get_adjusted_available_points(self):
        """ Gets only the points for credits that have not been labelled as Not Applicable """
        score = 0
        for sub in self.subcategorysubmission_set.all():
            score += sub.get_adjusted_available_points()
        return score
        
    def get_not_started_credit_count(self):
        """ Get the number of credits that have been marked complete, not pursuing, or not applicable """
        count = 0
        for sub in self.subcategorysubmission_set.all():
            count += sub.get_not_started_credit_count()
        return count

    def get_finished_credit_count(self):
        """ Get the number of credits that have been marked complete, not pursuing, or not applicable """
        count = 0
        for sub in self.subcategorysubmission_set.all():
            count += sub.get_finished_credit_count()
        return count
               
    def get_percent_complete(self):
        """ Return the percentage of credits completed in this category: 0 - 100 """
        total_credits = self.get_total_credits()
        if total_credits == 0: return 0
        return int((self.get_finished_credit_count() / float(total_credits)) * 100)

    def get_status(self):
        """ Returns a status label for this category or None if not started. """
        complete = self.get_percent_complete()
        return None if complete==0 else "Complete" if complete==100 else "In Progress"

    def get_progress_title(self):
        """ Returns a title for a progress summary on this category """
        return "Complete" if self.get_percent_complete() == 100 else "Progress"
        
    def is_innovation(self):
        return self.category.is_innovation()
       
class SubcategorySubmission(models.Model):
    """
        A Category from a credit set that is being submitted
    """
    category_submission = models.ForeignKey(CategorySubmission)
    subcategory = models.ForeignKey(Subcategory)

    class Meta:
        unique_together = ("category_submission", "subcategory")
        ordering = ("subcategory__ordinal",)
    
    def __unicode__(self):
        return unicode(self.subcategory)
        
    def get_crumb_label(self):
        return str(self)
    
    def get_id(self):
        """ Return a valid identifier representing this subcategory """
        return get_id(self)
     
    def get_institution(self):
        return self.category_submission.get_institution()
        
    def get_parent(self):
        """ Used for building crumbs """
        return self.category_submission
        
    def get_creditset(self):
        return self.category_submission.get_creditset()
    
    def get_total_credits(self):
        return self.subcategory.credit_set.count()
        
    def get_submit_url(self):
        return self.subcategory.get_submit_url()
        
    def get_scorecard_url(self):
        return '%s%s'%(self.category_submission.submissionset.get_scorecard_url(),self.subcategory.get_browse_url())

    def get_complete_credit_count(self):
        """ Find all CreditSubmissions in this subcategory that are complete """
        return self.creditusersubmission_set.filter(submission_status='c').count()
        
    def get_pending_credit_count(self):
        return self.creditusersubmission_set.filter(submission_status='p').count()
        
    def get_not_pursuing_credit_count(self):
        return self.creditusersubmission_set.filter(submission_status='np').count()
        
    def get_not_applicable_credit_count(self):
        return self.creditusersubmission_set.filter(submission_status='na').count()
        
    def get_not_started_credit_count(self):
        return self.creditusersubmission_set.filter(submission_status='ns').count()
        
    def get_finished_credit_count(self):
        """ Get the number of credits that have been marked complete, not pursuing, or not applicable """
        return self.creditusersubmission_set.exclude(submission_status='ns').exclude(submission_status='p').count()
    
    def get_claimed_points(self):
        score = 0
        for credit in self.creditusersubmission_set.filter(submission_status='c'):
            score += credit.assessed_points
        return score
        
    def get_available_points(self):
        points = 0
        for credit in self.subcategory.credit_set.all():
            points += credit.point_value
        return points
        
    def get_adjusted_available_points(self):
        """ Gets only the points for credits that have not been labelled as Not Applicable """
        score = 0
        for credit_submission in self.creditusersubmission_set.all():
                score += credit_submission.get_adjusted_available_points()
        return score
        
    def get_percent_complete(self):
        """ Return the percentage of credits completed in this subcategory: 0 - 100 """
        total_credits = self.subcategory.credit_set.count()
        if total_credits == 0: return 0
        return int((self.get_finished_credit_count() / float(total_credits)) * 100)

    def get_status(self):
        """ Returns a status label for this subcatogory or None if not started. """
        complete = self.get_percent_complete()
        return None if complete==0 else "Complete" if complete==100 else "In Progress"

    def get_progress_title(self):
        """ Returns a title for a progress summary on this subcatogory """
        return "Complete" if self.get_percent_complete() == 100 else "Progress"
       
    def is_innovation(self):
        return self.category_submission.is_innovation()

class ResponsibleParty(models.Model):
    """
        Stores responsible parties for institutions
    """
    institution = models.ForeignKey(Institution)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    department = models.CharField(max_length=128)
    email = models.EmailField()
    phone = PhoneNumberField()
    
    class Meta:
        ordering = ('last_name', 'first_name')
        verbose_name_plural = "Responsible Parties"
        
    def __unicode__(self):
        return "%s, %s" % (self.last_name, self.first_name)
        
class CreditSubmission(models.Model):
    """
        A complete submission data set for a credit
        This is really an abstract base class for two types of submissions:
         - a User Submission (normal submission for an institutions STARS submission set)
         - a Test Submission (a test case used to validate formulae in the Credit Editor)
    """
    credit = models.ForeignKey(Credit)

    class Meta:
        ordering = ("credit__type", "credit__ordinal",)

    def __unicode__(self):
        return unicode(self.credit)
       
#    @staticmethod
    def model_name():
        return u"Credit Submission" 
    model_name = staticmethod(model_name)

    def __init__(self, *args, **kwargs):
        super(CreditSubmission, self).__init__(*args, **kwargs)
        self.submission_fields = None  # lazy init
        
    def get_crumb_label(self):
        return str(self)
        
    def get_scorecard_url(self):
        return self.subcategory.get_scorecard_url(self.category_submission.submissionset)
    
    def get_institution(self):
        return self.subcategory_submission.get_institution()
        
    def get_submission_fields(self):
        """ 
            Returns the list of documentation field submission objects for this credit submission
            You can't simply ask self.documentationfieldsubmission_set.all() because each field may have a different type.
            If this CreditSubmission persists in DB, this method also saves empty submission field records for any that are missing.
            @return the complete list of DocumentationFieldSubmission sub-class objects related to this CreditSubmission
        """
        if (self.submission_fields):  # lazy init.
            return self.submission_fields
        
        documentation_field_list = self.credit.documentationfield_set.all()
        
        # Create the list of submission fields.
        errors = False
        
        submission_field_list = []
        for field in documentation_field_list:
            SubmissionFieldModelClass = DocumentationFieldSubmission.get_field_class(field)
            if SubmissionFieldModelClass:
                try:
                    submission_field = SubmissionFieldModelClass.objects.get(documentation_field=field, credit_submission=self)
                    # ORM / Model Inheritance issue:
                    #   DocumentationFieldSubmission has a foreign key to CreditSubmission, but object may have reference to a sub-class!
                    #   Hack: (Joseph)  update the reference in the field we just loaded.
                    submission_field.credit_submission = self
                    
                except SubmissionFieldModelClass.DoesNotExist:
                    submission_field = SubmissionFieldModelClass(documentation_field=field, credit_submission=self)
                    submission_field.save()
                submission_field_list.append(submission_field)
                
        self.submission_fields = submission_field_list
        return self.submission_fields
    
    def get_submission_field_values(self):
        """ Returns the list of documentation field values for this submission """
        return [field.get_value() for field in self.get_submission_fields()]    

    def get_submission_field_key(self):
        """ Returns a dictionary with identifier:value for each submission field """
        fields = self.get_submission_fields()
        key = {}
        for field in fields:
            key[field.documentation_field.identifier] = field.get_value()
        return key
        
    def print_submission_fields(self):
        import sys
        print >> sys.stderr, "Fields for CreditSubmission: %s"%self.__str__()
        fields = self.get_submission_fields()
        for field in fields:
            print >> sys.stderr, field

    # @todo: rename or remove this - potential confusion b/c name conflict with CreditUserSubmission!!
    #        I don't think this one is actually called anywhere.
    def is_complete(self):
        """ Return True if the Credit Submission is complete."""
        if not self.persists(): # New submissions are incomplete - don't try to access fields yet!
            return False
        for field in self.get_submission_fields():
            if field.documentation_field.is_required() and not field.value:
                return False
        # assert: all required fields contain a value.
        return True
    
    def persists(self):
        """Does this CreditSubmission persist in the DB?"""
        return (not self.pk == None)
        
    def get_available_points(self):
        return self.credit.point_value

    @staticmethod
    def round_points(points, log_error=True):
        """ 
            Convert points to numeric and round to the correct # decimals 
            Returns (points, error) where
                - points = rounded numeric point value (or 0 if an error occurred) 
                - error = error message  or None if conversion was successful
        """
        try: # Ensure that the result of the formula was a valid points value!
            points = float(points)
            return (round(points,2), None)
        except Exception, e:
            if log_error:
                watchdog.log("Submission", "Error converting formula result (%s) to numeric type : %s"%(points.__str__(),e), watchdog.ERROR)
            return (0, "Non-numeric result calculated for points: %s"%points)
        
    def validate_points(self, points, log_error=True):
        """ 
             Helper: Validate the points calculated for this submission 
             Returns (points, messages), where points are the validated points 
               - message is a list of error messages associated with any validation errors,
                  which is empty if the the points validated.
        """
        messages = []
                
        points, numeric_error = self.round_points(points, log_error)      # is it numeric
        if numeric_error:
            messages.append(numeric_error)
                
        if points<0 or points>self.credit.point_value:  # is it in range?
            range_error = ( "Points (%s) are out of range (0 - %s)."%(points.__str__(), self.credit.point_value) )
            if log_error:
                watchdog.log("Submission", range_error, watchdog.ERROR)
            messages.append(range_error)
            points = 0
            
        return points, messages
        
#    def __str__(self):  #  For DEBUG - comment out __unicode__ method above
#        if self.persists(): persists="persists"
#        else: persists="not saved"
#        return "<CreditSubmission %s credit_id=%s  %s>"%(self.id, self.credit.id, persists)


CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED = [
    ('c', 'Pursuing'),
    ('p', 'In Progress'),
    ('np', 'Not Pursuing'),
]

# The 'ns' option isn't accessible in forms and 'na' only sometimes, so we 3 different lists.
CREDIT_SUBMISSION_STATUS_CHOICES_W_NA = list(CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED)
CREDIT_SUBMISSION_STATUS_CHOICES_W_NA.append(('na', 'Not Applicable'))
CREDIT_SUBMISSION_STATUS_CHOICES = list(CREDIT_SUBMISSION_STATUS_CHOICES_W_NA)
CREDIT_SUBMISSION_STATUS_CHOICES.append(('ns', 'Not Started'))

CREDIT_SUBMISSION_STATUS_ICONS = {   # used by template tag to create iconic representation of status
    'c'  : ('tick.png', 'c'),
    'p'  : ('pencil.png', '...'),
    'np' : ('grey_cross.png', '-'),
    'na' : ('tag_yellow.png', '-'),
}

class CreditUserSubmission(CreditSubmission):
    """
        An individual submitted credit for an institutions STARS submission set
    """
    subcategory_submission = models.ForeignKey(SubcategorySubmission)
    assessed_points = models.FloatField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    submission_status = models.CharField(max_length=8, choices=CREDIT_SUBMISSION_STATUS_CHOICES, default='ns')
    review_status = models.CharField(max_length=8)
    applicability_reason = models.ForeignKey(ApplicabilityReason, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    internal_notes = models.TextField(help_text='This field is useful if you want to store notes for other people in your organization regarding this credit. They will not be published.', blank=True, null=True)
    submission_notes = models.TextField(help_text='Use this space to add any additional information you may have about this credit. This will be published along with your submission.', blank=True, null=True)
    responsible_party_confirm = models.BooleanField()
    responsible_party = models.ForeignKey(ResponsibleParty, blank=True, null=True)

    class Meta:
        # @todo: the unique clause needs to be added at the DB level now :-(
#        unique_together = ("subcategory_submission", "credit")
        pass
    
    def get_submit_url(self):
        return self.credit.get_submit_url()
        
    def get_scorecard_url(self):
        return self.credit.get_scorecard_url(self.subcategory_submission.category_submission.submissionset)

    def get_parent(self):
        """ Used for building crumbs """
        return self.subcategory_submission
        
    def get_creditset(self):
        return self.subcategory_submission.get_creditset()

    def is_finished(self):
        """ Indicate if this credit has been marked anything other than pending or not started """
        return self.submission_status != 'p' and self.submission_status != 'ns' and self.submission_status != None

    def save(self):
        """ Override model.Model save() method to update credit status"""
        self.last_updated = datetime.now()
        self.assessed_points = float( self._calculate_points() )
        
        super(CreditUserSubmission, self).save()

    def is_complete(self):
        return self.submission_status == 'c'
    
    def is_na(self):
        return self.submission_status == 'na'

    def is_pursued(self):
        """ Returns False if this credit is marked 'na' or 'np'  """
        return self.submission_status != 'na' and self.submission_status != 'np'
    
    def mark_as_in_progress(self):
        self.submission_status = 'p'

#    def __str__(self):  # For DEBUG - comment out __unicode__ method above
#        return "<CreditUserSubmission:  %s>"%super(CreditUserSubmission,self).__str__()
            
    def get_adjusted_available_points(self):
        """ Gets only the points for credits that have not been labelled as Not Applicable """
        if self.submission_status == "na":
            return 0
        return self.credit.point_value

    def _calculate_points(self):
        """ Helper: returns the number of points calculated for this submission"""
        # Somewhat complex logic is required here so that i something goes wrong,
        #   we log a detailed message, but only show the user meaningful messages.
        if not self.is_complete(): # no points for incomplete submission
            return 0
        assessed_points = 0  # default is zero - now re-calculate points...
        validation_error = False
        
        (ran, message, exception, points) = self.credit.execute_formula(self)

        if ran:  #perform validation on points...
            (points, messages) = self.validate_points(points)
            validation_error = len(messages) > 0
            
        if not ran or validation_error:  #. Provide a generic message for user...
            flashMessage.send("There was an error processing this credit. AASHE has noted the error and will work to resolve the issue.", flashMessage.ERROR)  
        else:
            assessed_points = points
            
        return assessed_points
    
class CreditTestSubmission(CreditSubmission):
    """
        A test data set for a Credit formula - not part of any submission set
    """
    expected_value = models.FloatField(blank=True, null=True, help_text="Point value expected from the formula for this test data")

#    @staticmethod
    def model_name():
        return u"Formula Test Case" 
    model_name = staticmethod(model_name)

    def __unicode__(self):
        return "Formula Test Case for %s:="%unicode(self.credit)

    def run_test(self):
        """ 
        Run this test case on the given test data
        @param fields  array of field data for the test case.
        @return: (had_error, messages), where 
                   - had_error is true if there was an error executing the test;
                   - messages is a list of error messages
                 Also sets computed_value and test fields in this object.
        """
        self.result = False
        self.computed_value = None
        messages = []
        had_error = False
        (ran, msg, exception, points) = self.credit.execute_formula(self)
        if ran:
            try:
                self.expected_value = float(self.expected_value)   # are we expecting a numeric result?
                (self.computed_value, messages) = self.validate_points(points) 
                self.result = (abs(self.computed_value - self.expected_value) < 0.00001)  # Floating point equality to 5rd decimal place
            except (TypeError, ValueError):  # we're not expecting result to be numeric...
                self.computed_value = points
                self.result = self.computed_value == self.expected_value
        else:
            # Since this is test, substitute user-friendly message for real error message.
            if isinstance(exception,AssertionError): 
                messages.append('Assertion Failed: %s'%exception)
            elif exception:
                messages.append('Formula Error: %s'%exception)  
            else:
                messages.append(msg)            

        return (len(messages)>0, messages)   
    
    def reset_test(self):
        """ reset this test such that the computed_value is None """ 
        self.computed_value = None
        self.result = self.expected_value == self.computed_value
        
    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.credit
    
    def get_edit_url(self):
        return "%s%d/" % (self.credit.get_formula_url(), self.id)
     
    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sdelete/" % self.get_edit_url()

    def get_add_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sadd-test/" % (self.credit.get_formula_url(),)

    def parameter_list(self):
        """ Returns a string with this submission's field values formatted as a parameter list """
        return ', '.join([field.__str__() for field in self.get_submission_fields()])

    def __unicode__(self):
        return "f( %s ) = %s" % (self.parameter_list(), self.expected_value)

    def __str__(self):
        return "<CreditTestSubmission: expected=%s  %s>"%(self.expected_value, super(CreditTestSubmission,self).__str__() )

"""        
DOCUMENTATION_FIELD_TYPES = (
    ('text', 'text'),
    ('long_text', 'long text'),
    ('numeric', 'numeric'),
    ('boolean', 'yes/no'),
    ('choice', 'choose one'),
    ('multichoice', 'choose many'),
    ('url', 'url'),
    ('date', 'date'),
    ('upload', 'upload'),
    ('multiple_upload', 'multiple upload'),
)
"""

class DocumentationFieldSubmission(models.Model):
    """
        The submitted value for a documentation field (abstract).
    """
    documentation_field = models.ForeignKey(DocumentationField, related_name="%(class)s_set")
    credit_submission = models.ForeignKey(CreditSubmission)
    
    class Meta:
        abstract = True
        unique_together = ("documentation_field", "credit_submission")
        
    def __unicode__(self):
        """ return the title of this submission field """
        return self.documentation_field.__unicode__()

    def __str__(self):
        """ return a string representation of the submission' value """
        return str(self.get_value())
    
    def get_parent(self):
        """ Used for building crumbs """
        return self.credit_submission
        
    def get_institution(self):
        return self.credit_submission.get_institution()
        
    def get_creditset(self):
        return self.credit_submission.get_creditset()

    def persists(self):
        """Does this Submission object persist in the DB?"""
        return (not self.pk == None)
        
#    @staticmethod
    def get_field_class(field):
        """
            Returns the related DocumentationFieldSubmission model class for a particular documentation field
        """
        if field.type == 'text':
            return TextSubmission
        if field.type == 'long_text':
            return LongTextSubmission
        if field.type == 'numeric':
            return NumericSubmission
        if field.type == 'choice':
            return ChoiceWithOtherSubmission if field.has_other_choice() else ChoiceSubmission
        if field.type == 'multichoice':
            return MultiChoiceWithOtherSubmission if field.has_other_choice() else MultiChoiceSubmission
        if field.type == 'boolean':
            return BooleanSubmission
        if field.type == 'url':
            return URLSubmission
        if field.type == 'date':
            return DateSubmission
        if field.type == 'upload':
            return UploadSubmission
       
        return None
    get_field_class = staticmethod(get_field_class)

    def save(self):
        """ Override models.Model save() method to forstall save if CreditSubmission doesn't persist"""
        # Only save submission fields if the overall submission has been saved.
        if self.credit_submission.persists():
            super(DocumentationFieldSubmission, self).save()

    def get_value(self):
        """ Use this accessor to get this submission's value - rather than accessing .value directly """
        return self.value

    def get_units(self):
        """ Return the units associated with the field for this submission """
        return self.documentation_field.get_units()
        
    def is_empty(self):
        if self.value == None or self.value == "":
            return True
        # if it's nothing but whitespace
        if re.match("\s+", self.value) != None:
            return True
        return False
    

class AbstractChoiceSubmission(DocumentationFieldSubmission):
    class Meta:  
        abstract = True

    def __str__(self):
        """ return a string representation of the submission' value """
        choice = self.get_value()
        return self._get_str(choice)

    @staticmethod
    def _get_str(choice):
        return '<%d:%s>'%(choice.ordinal, choice.choice) if choice else '<None>'
        
    def get_choice_queryset(self):
        """ Return the queryset used to define the choices for this submission """
        return Choice.objects.filter(documentation_field=self.documentation_field).filter(is_bonafide=True)

    def get_last_choice(self):
        """ Return the last Choice object in the list of choices for this submission """
        choices = self.get_choice_queryset()
        if len(choices) > 0:
            return choices[len(choices)-1]  # no negative indexing on QuerySets
        else:
            return None
    
class ChoiceSubmission(AbstractChoiceSubmission):
    """
        The submitted value for a Single Choice Documentation Field
    """
    value = models.ForeignKey(Choice, blank=True, null=True)
    
    def get_value(self):
        """ Value is a Choice object, or None """
        return self.value

class AbstractChoiceWithOther(object):
    """ A base class for sharing the compress / decompress logig needed for Choice-with-other type submisssions """
    def compress(self, choice, other_value):
        """
            Given a decompressed choice / other value pair into a single Choice value
            Return a single Choice representing the selection, or None.
            Assumes choice is a Choice and other_value has been properly sanatized!
            See decompress() above, except compress is peformed during clean() in ModelChoiceWithOtherField
        """
        if not choice:
            return None
        if choice == self.get_last_choice() and other_value:  #The value is an 'other' - create the Choice object
            # search for the 'other' choice value first - try to re-use an existing choice.
            find = Choice.objects.filter(documentation_field=self.documentation_field).filter(choice=other_value)  #@todo: can this be case insensitive?
            if len(find) > 0:
                choice = find[0]
            else:
                choice = Choice(documentation_field=self.documentation_field, choice=other_value, is_bonafide = False)
                choice.save()

        return choice

    
class ChoiceWithOtherSubmission(ChoiceSubmission, AbstractChoiceWithOther):
    """ A proxy model (does not create a new table) for a Choice Submission with an 'other' choice """
    class Meta:
        proxy = True

    def decompress(self, value):
        """ 
            Given a single value (the pk for a Choice object), 
            return a list of the form: [choiceId, otherValue], where
             - choiceId is the id of the selection choice and otherValue is the the text value of 
               the choice, if it is a non-bonafide (other) choice.
            This is really the decompress logic for a ChoiceWithOtherSelectWidget (MutliWidget), 
              but needs to do "model"-type stuff, so it is passed to the widget via the form.
        """
        if not value:
            return [None, None]
        # The choice must be in the DB - this algorithm is not foolproof - could use a little more thought.
        try:
            choice = Choice.objects.get(id=value)
        except:
            watchdog.log("Submissions", "Attempt to decompress non-existing Choice (id=%s)"%value, watchdog.ERROR)
            return [None, None]
        if choice.is_bonafide:  # A bonafide choice is one of the actual choices
            return [value, None]
        else:                   # whereas non-bonafide choices represent an 'other' choice.
            # value is not one of the bonafide choices - try to find it in the DB.
            # The selection is the last choice, and the Choice text is the 'other' field.
            return [self.get_last_choice().pk, choice.choice ]

    def compress(self, choice, other_value):
        """
            Given a decompressed choice / other value pair into a single Choice value
            Return a single Choice representing the selection, or None.
            Assumes choice is a Choice and other_value has been properly sanatized!
            See decompress() above, except compress is peformed during clean() in ModelChoiceWithOtherField
        """
        # Warn the user about potentially lost data
        last_choice = self.get_last_choice()
        if other_value and choice != last_choice:
            flashMessage.send("Warning: '%s' will not be saved because '%s' was not selected."%(other_value, last_choice.choice), flashMessage.NOTICE)
        return super(ChoiceWithOtherSubmission, self).compress(choice, other_value)

            
class MultiChoiceSubmission(AbstractChoiceSubmission):
    """
        The submitted value for a Multi-Choice Documentation Field
    """
    # should be called values, really, since it potentially represents multiple values
    value = models.ManyToManyField(Choice, blank=True, null=True)
    
    def get_value(self):
        """ Value is a list of Choice objects, or None """
        # got to be careful here - many-to-many is only valid after submission has been saved.
        return self.value.all() if self.persists() else None 

    def __str__(self):
        """ return a string representation of the submission' value """
        choices = self.get_value()
        if not choices:
            return "[ ]"
        return '[%s]' %','.join([self._get_str(choice) for choice in choices])
    

class MultiChoiceWithOtherSubmission(MultiChoiceSubmission, AbstractChoiceWithOther):
    """ A proxy model (does not create a new table) for a MultiChoice Submission with an 'other' choice """
    class Meta:
        proxy = True
        
    def decompress(self, value):
        """ 
            Given a list of values (list of pk for  Choice objects), 
            return a list of the form: [[choiceId1, choiceId2], otherValue], where
             - choiceId's are the id's of the selected choices and otherValue is the the text value of 
               the choice, if it is a non-bonafide (other) choice.
            This is really the decompress logic for a SelectMultipleWithOtherWidget (MutliWidget), 
              but needs to do "model"-type stuff, so it is passed to the widget via the form.
        """
        if not value:
            return [[], None]
        # The choice must be in the DB - this algorithm is not foolproof - could use a little more thought.
        choice_list=[]
        other = None
        for choice_id in value:
            try:
                choice = Choice.objects.get(id=choice_id)
            except:
                watchdog.log("Submissions", "Attempt to decompress non-existing Choice (id=%s)"%choice_id, watchdog.ERROR)
                return [[], None]
            if not choice.is_bonafide:  # An 'other'  choice replace the choice with the last choice.
                if other:
                    watchdog.log("Submissions", "Found multiple 'other' choices (%s and %s) associated with single MultiChoiceWithOtherSubmission (id=%s)"%other, choice.choice, self_id, watchdog.ERROR)
                else:
                    choice_id = self.get_last_choice().pk
                    other = choice.choice
            choice_list.append(choice_id)
        
        return [choice_list, other]
    
    def compress(self, choices, other_value):
        """
            Given a decompressed choice list / other value pair into a single Choice list
            Return a list of Choices representing the selections, or None.
            Assumes choices is a list of Choices and other_value has been properly sanatized!
            See decompress() above, except compress is peformed during clean() in ModelMultipleChoiceWithOtherField
        """
        choice_list = []
        for choice in choices:
            choice_list.append( super(MultiChoiceWithOtherSubmission, self).compress(choice, other_value) )
             
        # Warn the user about potentially lost data
        last_choice = self.get_last_choice()
        if other_value and not last_choice in choices:
            flashMessage.send("Warning: '%s' will not be saved because '%s' was not selected."%(other_value, last_choice.choice), flashMessage.NOTICE)

        return choice_list


class URLSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a URL Documentation Field
    """
    value = models.URLField(blank=True, null=True)
        
class DateSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Date Documentation Field
    """
    value = models.DateField(blank=True, null=True)
    
class NumericSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Numeric Documentation Field
    """
    value = models.FloatField(blank=True, null=True)

class TextSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Text Documentation Field
    """
    value = models.CharField(max_length=255, blank=True, null=True)

class LongTextSubmission(DocumentationFieldSubmission):
    """
        The submitted value for Long Text Documentation Field
    """
    value = models.TextField(blank=True, null=True)
    
    
def upload_path_callback(instance, filename):
    """
        Dynamically alters the upload path based on the instance
        secure/<org_id>/<creditset_id>/<credit_id>/<field_id>/<file_name>.<ext>
    """
    
    if instance.credit_submission.__class__.__name__ == "CreditUserSubmission":
        field = instance.documentation_field
        credit = field.credit
        creditset = field.credit.subcategory.category.creditset
        institution = instance.get_institution()
        path = "secure/%d/%d/%d/%d/%s" % (institution.id, creditset.id, credit.id, field.id, filename)
        return path
    else:
        # if this is a test submission use a different URL
        return "uploads/test_cases/%s" % filename

class UploadSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a File Upload Documentation Field
        @todo: custom storage engine to rename files
    """
    value = models.FileField(upload_to=upload_path_callback, blank=True, null=True)
    
    def get_filename(self):
        """ Returns the name of the file w/out the full path. """
        return os.path.basename(self.value.name)
    
class BooleanSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Boolean Documentation Field
    """
    value = models.NullBooleanField(blank=True, null=True)
    
    def __unicode__(self):
        if self.value == True:
            return "Yes"
        elif self.value == False:
            return "No"
        else:
            return "---"
        
PAYMENT_REASON_CHOICES = (
    ('reg', 'registration'),
    ('submit', 'submission'),
    ('extend', 'extension'),
)

PAYMENT_TYPE_CHOICES = (
    ('credit', 'credit'),
    ('check', 'check'),
    ('later', 'pay later'),
)

PAYMENT_TYPE_ICONS = {   # used by template tag to create iconic representation of paymnet
    'credit'  : ('creditcards.png', 'Paid by credit'),
    'check'  : ('check.png', 'Paid by check'),
    'later' : ('flag_red.png', 'Awaiting payment'),
}

class Payment(models.Model):
    """
        Any payment associated with submissions such as registration
    """
    submissionset = models.ForeignKey(SubmissionSet)
    date = models.DateTimeField()
    amount = models.FloatField()
    user = models.ForeignKey(User)
    reason = models.CharField(max_length='8', choices=PAYMENT_REASON_CHOICES)
    type = models.CharField(max_length='8', choices=PAYMENT_TYPE_CHOICES)
    confirmation = models.CharField(max_length='16', blank=True, null=True, help_text='The CC confirmation code or check number')
    
    def __unicode__(self):
        return "%s $%.2f" % (self.date, self.amount)

    @classmethod
    def get_manage_url(cls):
        return "%spayments/"%settings.MANAGE_INSTITUTION_URL
        
    @classmethod
    def get_admin_url(cls):
        return "%spayments/"%settings.ADMIN_URL
        
    def get_admin_institution_url(self):
        return self.submissionset.institution.get_admin_payments_url()

    def get_edit_url(self):
        return "%s%d/edit/" % (self.get_admin_url(), self.id)
     
    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%s%d/delete/" % (self.get_admin_url(), self.id)
        
    def get_receipt_url(self):
        """ Returns a URL for the page where staff can send a receipt """
        return "%s%d/receipt/" % (self.get_admin_url(), self.id)
    
    def get_institution(self):
        return self.submissionset.institution

