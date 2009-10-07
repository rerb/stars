from datetime import datetime
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe 

from stars.apps.credits.models import *
from stars.apps.institutions.models import *
from stars.apps.helpers import watchdog
from stars.apps.helpers import flashMessage
from stars.apps.helpers import managers

class Rating(models.Model):
    """
        The official stars ratings, such as Gold, Silver, Bronze
    """
    name = models.CharField(max_length='16')
    ordinal = models.SmallIntegerField()
    
    class Meta:
        ordering = ('-ordinal',)
    
    def __unicode__(self):
        return self.name

SUBMISSION_STATUS_CHOICES = (
    ('r', 'Rated'),
    ('ps', 'Pending Submission'),
    ('pr', 'Pending Review'),
)

class SubmissionSet(models.Model):
    """
        A creditset (ex: 1.0) that is being submitted
    """
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
    
    def __unicode__(self):
        return unicode(self.creditset)
        
    def get_status(self):
        if self.status == 'r':
            return unicode(self.rating)
        return self.get_status_display()
        
    def get_admin_url(self):
        return "%ssubmissionsets/%d/" % (self.institution.get_admin_url(), self.id)
        
    def get_manage_url(self):
        return "/dashboard/manage/submissionsets/%d/" % (self.id)
        
    def get_submit_url(self):
        return self.creditset.get_submit_url()
        
    def get_parent(self):
        """ Used for building crumbs """
        return None
        
    def get_total_credits(self):
        total = 0
        for cat in self.creditset.category_set.all():
            for sub in cat.subcategory_set.all():
                total += sub.credit_set.count()
        return total
    
    def get_claimed_score(self):
        """
            @TODO: Consider changing this to a stored value in the model
            if we do that we'll probably need transactions
        """
        score = 0
        for cat in self.categorysubmission_set.all():
            for sub in cat.subcategorysubmission_set.all():
                for credit in sub.creditusersubmission_set.filter(submission_status='c'):
                    score += credit.assessed_points
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
        return "Complete" if self.get_percent_complete() == 100 else "Progress"


def get_active_submissions(category=None, subcategory=None, credit=None):
    """ Return a queryset for ALL active (started / finished) credit submissions that meet the given criteria.
        Only ZERO or ONE criteria should be specified - more is redundant and this code does not check for consistency.
    """
    submissions = CreditUserSubmission.objects.all()

    if credit:
        submissions = submissions.filter(credit=credit)
    else:
        # This code results in a nested query. May not be optimized in MySQL - see Performance Considerations at: http://docs.djangoproject.com/en/dev/ref/models/querysets/#in
        subcategory_submission_set = None
        if subcategory:
            subcategory_submission_set = SubcategorySubmission.objects.filter(subcategory=subcategory)
        elif category:
            category_submissions = CategorySubmission.objects.filter(category=category)
            subcategory_submission_set = SubcategorySubmission.objects.filter(category_submission__in=category_submissions)
        if subcategory_submission_set:
            submissions = submissions.filter(subcategory_submission__in=subcategory_submission_set)

    return submissions.exclude(submission_status='ns')        

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
        
    def get_total_credits(self):
        total = 0
        for sub in self.category.subcategory_set.all():
            total = total + sub.credit_set.count()
        return total

    def get_parent(self):
        """ Used for building crumbs """
        return self.submissionset
        
    def get_submit_url(self):
        return self.category.get_submit_url()
        
    def get_claimed_score(self):
        score = 0
        for sub in self.subcategorysubmission_set.all():
            score += sub.get_claimed_score()
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
        
    def get_parent(self):
        """ Used for building crumbs """
        return self.category_submission
        
    def get_submit_url(self):
        return self.subcategory.get_submit_url()
        
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
        
    def get_claimed_score(self):
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
        
    def get_finished_credit_count(self):
        """ Get the number of credits that have been marked complete, not pursuing, or not applicable """
        count = 0
        for credit in self.creditusersubmission_set.all():
            if credit.is_finished():
                count += 1
        return count
    
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
       

CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED = [
    ('c', 'Complete'),
    ('p', 'In Progress'),
    ('np', 'Not Pursuing'),
]

# The 'ns' option isn't accessible in forms and 'na' only sometimes, so we 3 different lists.
CREDIT_SUBMISSION_STATUS_CHOICES_W_NA = list(CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED)
CREDIT_SUBMISSION_STATUS_CHOICES_W_NA.append(('na', 'Not Applicable'))
CREDIT_SUBMISSION_STATUS_CHOICES = list(CREDIT_SUBMISSION_STATUS_CHOICES_W_NA)
CREDIT_SUBMISSION_STATUS_CHOICES.append(('ns', 'Not Started'))

CREDIT_SUBMISSION_STATUS_ICONS = {
    'c'  : ('complete.png', 'c', 'Complete'),
    'p'  : ('in_progress.gif', '...', 'In Progress'),
    'np' : ('na.png', '-', 'Not Pursuing'),
    'na' : ('na.png', '-', 'Not Applicable')
}
def _get_status_icon_tag(status):
    """ Returns an image tag, marked safe, and text for displaying a submission status """
    if (status == 'ns'):
        return '', ''  # no image, no text for Not Started status
    
    ### THIS IS HIDEOUS - how can I pass the icon, title, & alt to a template for rendering?
    icon_file, alt, title = CREDIT_SUBMISSION_STATUS_ICONS[status] 
    src = "%s%s%s/"%(settings.MEDIA_URL,"static/images/", icon_file)
    return mark_safe( "<img src='%s' alt='%s' title='%s'> "%(src, alt, title) ), title
        
class CreditSubmission(models.Model):
    """
        A complete submission data set for a credit
        This is really an abstract base class for two types of submissions:
         - a User Submission (normal submission for an institutions STARS submission set)
         - a Test Submission (a test case used to validate formulae in the Credit Editor)
    """
    credit = models.ForeignKey(Credit)

    class Meta:
        ordering = ("credit__ordinal",)
    
#    @staticmethod
    def model_name():
        return u"Credit Submission" 
    model_name = staticmethod(model_name)

    def __init__(self, *args, **kwargs):
        super(CreditSubmission, self).__init__(*args, **kwargs)
        self.submission_fields = None  # lazy init
        
    def __unicode__(self):
        return unicode(self.credit)
        
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
        fields = self.get_submission_fields()
        values = []
        for field in fields:
            values.append(field.get_value())
        return values

    def get_submission_field_key(self):
        """ Returns a dictionary with identifier:value for each submission field """
        fields = self.get_submission_fields()
        key = {}
        for field in fields:
            key[field.documentation_field.identifier] = field.get_value()
        return key
        
    def print_submission_fields(self):
        print "Fields for CreditSubmission: %s"%self.__str__()
        fields =self.get_submission_fields()
        for field in fields:
            print field

    def is_complete(self):
        """ Return True if the Credit Submission is complete."""
        if not self.persists(): # New submissions are incomplete - don't try to access fields yet!
            return False
        for field in self.get_submission_fields():
            if field.documentation_field.is_required and not field.value:
                return False
        # assert: all required fields contain a value.
        return True
    
    def persists(self):
        """Does this CreditSubmission persist in the DB?"""
        return (not self.pk == None)
        
    def get_available_points(self):
        return self.credit.point_value
    
    def __str__(self):  #  For DEBUG - comment out __unicode__ method above
        if self.persists(): persists="persists"
        else: persists="not saved"
        return "<CreditSubmission %s credit_id=%s  %s>"%(self.id, self.credit.id, persists)

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
    internal_notes = models.TextField(help_text='This field is useful if you want to store notes for other people in your organization regarding this credit. They will not be published.')
    submission_notes = models.TextField(help_text='Use this space to add any additional information you may have about this credit. This will be published along with your submission.')

    class Meta:
        # @todo: the unique clause needs to be added at the DB level now :-(
#        unique_together = ("subcategory_submission", "credit")
        pass
    
    def get_submit_url(self):
        return self.credit.get_submit_url()
        
    def get_parent(self):
        """ Used for building crumbs """
        return self.subcategory_submission

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
    
    def mark_as_in_progress(self):
        self.submission_status = 'p'

    def __str__(self):  # For DEBUG - comment out __unicode__ method above
        return "<CreditUserSubmission:  %s>"%super(CreditUserSubmission,self).__str__()
            
    def get_status_display(self):
        """ Replaces get_submission_status_display, added by Django, to include an icon """
        icon, text = _get_status_icon_tag(self.submission_status)
        return mark_safe("%s%s"%(icon, text))

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
        (ran, message, exception, points) = self.credit.execute_formula(self)
        if ran:
            try: # Ensure that the result of the formula was a valid points value!
                points = float(points)  # is it numeric?
                if points<0 or points>self.credit.point_value :  # is it in range?
                    message = "Points (%s) are out of range (0 - %s)."%(points.__str__(), self.credit.point_value)
                    watchdog.log("Submission", message, watchdog.ERROR)
                    ran = False
                else:  # finally... calculated points are valid...
                    assessed_points = points
            except Exception, e:
                message = "Non-numeric result calculated for points: %s"%points
                watchdog.log("Submission", "Error converting formula result (%s) to numeric type : %s"%(points.__str__(),e), watchdog.ERROR)
                ran = False
        else:
            watchdog.log("Submission", "Could not calculate points: %s"%exception, watchdog.NOTICE)

        if not ran:
            if message:
                flashMessage.send(message, flashMessage.ERROR)  
            flashMessage.send("Unable to compute points for this credit - please contact AASHE if problem persists", flashMessage.NOTICE)
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
        @return: (had_error, message), where had_error is true if there was an error executing the test, and message is the error message
                 Also sets computed_value and test fields in this object.
        """
        self.result = False
        self.computed_value = None
        (ran, message, exception, points) = self.credit.execute_formula(self)
        if ran:
            self.computed_value = points
        self.result = (self.computed_value == self.expected_value)
        # Since this is test, substitute user-friendly message for real error message.
        if isinstance(exception,AssertionError): 
            message = 'Assertion Failed: %s'%exception  
        elif exception:
            message = 'Formula Error: %s'%exception  
        
        return (not ran, message)   
    
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

    def field_values(self):
        return ','.join([str(field) for field in self.get_submission_field_values()])

    def __unicode__(self):
        return "f( %s ) = %s" % (self.field_values(), self.expected_value)

    def __str__(self):
        return "<CreditTestSubmission: expected=%s  %s>"%(self.expected_value, super(CreditTestSubmission,self).__str__() )

"""        
DOCUMENTATION_FIELD_TYPES = (
    ('url', 'url'),
    ('date', 'date'),
    ('numeric', 'numeric'),
    ('text', 'text'),
    ('long_text', 'long text'),
    ('upload', 'upload'),
    ('multiple_upload', 'multiple upload'),
    ('boolean', 'yes/no'),
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
        return self.documentation_field.title
    
    def get_parent(self):
        """ Used for building crumbs """
        return self.credit_submission

    def persists(self):
        """Does this Submission object persist in the DB?"""
        return (not self.pk == None)
        
#    @staticmethod
    def get_field_class(field):
        """
            Returns the related DocumentationFieldSubmission model class for a particular documentation field
        """
        # Choice fields are determined by the selection type rather than the field type - they always store a foreign key to a Choice
        if field.is_single_choice():
            if field.has_other_choice():
                return ChoiceWithOtherSubmission
            else:
                return ChoiceSubmission
        if field.is_multi_choice():
            if field.has_other_choice():
                return MultiChoiceWithOtherSubmission
            else:
                return MultiChoiceSubmission
        
        # @todo: form class name from constant, ala: FieldClass = getattr(SubmissionsForms, "%sSubmission" % SubClassName[field_type] , None)
        if field.type == 'url':
            return URLSubmission
        if field.type == 'date':
            return DateSubmission
        if field.type == 'numeric':
            return NumericSubmission
        if field.type == 'text':
            return TextSubmission
        if field.type == 'long_text':
            return LongTextSubmission
        if field.type == 'boolean':
            return BooleanSubmission
            
        return None
    get_field_class = staticmethod(get_field_class)

    def save(self):
        """ Override models.Model save() method to forstall save if CreditSubmission doesn't persist"""
        # Only save submission fields if the overall submission has been saved.
        if self.credit_submission.persists():
            super(DocumentationFieldSubmission, self).save()

    def mark_required(self):
        """ Should this field be marked as required? """
        return self.documentation_field.is_required and self.value == None
                
    def get_value(self):
        """ Use this accessor to get this submission's value - rather than accessing .value directly """
        return self.value
    
    def get_units(self):
        """ Return the units associated with the choices in this submission """
        return self.documentation_field.units
    
    def __str__(self):
        return "<Doc Field Sub. value = %s>" %self.get_value()

class AbstractChoiceSubmission(DocumentationFieldSubmission):
    class Meta:  
        abstract = True

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
    
class ChoiceWithOtherSubmission(ChoiceSubmission):
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
            print "Attempt to decompress non-existing ChoiceWithOther (id=%s)"%value
            watchdog.log("Submissions", "Attempt to decompress non-existing ChoiceWithOther (id=%s)"%value, watchdog.ERROR)
            return [None, None]
        if choice.is_bonafide:  # A bonafide choice is one of the actual choices
            return [value, None]
        else:                   # whereas non-bonafide choices represent an 'other' choice.
            # value is not one of the bonafide choices - try to find it in the DB.
            # The selection is the last choice, and the Choice text is the 'other' field.
            return [self.get_last_choice().pk, choice.choice ]
        
    def compress(self, choice, other_value):
        """
            Given a compressed the choice / other value pair into a single Choice value
            Return a single Choice representing the selection, or None.
            Assumes choice is a Choice and other_value has been properly sanatized!
            See decompress() above, except compress is peformed during clean() in ModelChoiceWithOtherField
            queryset is the QuerySet governing which bonafide choices are handled by the field.
        """
        if not choice:
            return None
        if choice == self.get_last_choice() and other_value:  #The value is an 'other' - create the Choice object
            # search for the 'other' choice value first - try to re-use an existing choice.
            find = Choice.objects.filter(choice=other_value)  #@todo: can this be case insensitive?
            if len(find) > 0:
                choice = find[0]
            else:
                choice = Choice(documentation_field=self.documentation_field, choice=other_value, is_bonafide = False)
            choice.save()

        return choice
            
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

class MultiChoiceWithOtherSubmission(MultiChoiceSubmission):
    """ A proxy model (does not create a new table) for a MultiChoice Submission with an 'other' choice """
    class Meta:
        proxy = True
        
    #@todo: Write the compress and decompress logic...
    def decompress(self, value):
        if not value:
            return [None, None]
        return [value, None]  
 
    def compress(self, choice, other_value):
        return choice
          
        
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

class UploadSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a File Upload Documentation Field
    """
    #value = models.FileField()  @TODO file handling
    
class BooleanSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Boolean Documentation Field
    """
    value = models.NullBooleanField(blank=True, null=True)

class InstitutionState(models.Model):
    """
        Used to track the current state of an institution such as the current submission set
    """
    institution = models.OneToOneField(Institution, related_name='state')
    active_submission_set = models.ForeignKey(SubmissionSet)

    def __unicode__(self):
        return unicode(self.institution)
    
        
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
    confirmation = models.CharField(max_length='16')
    
    def __unicode__(self):
        return "%s $%.2f" % (self.date, self.amount)
    