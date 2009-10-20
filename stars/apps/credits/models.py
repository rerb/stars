from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.encoding import smart_unicode

import re
from stars.apps.helpers import watchdog

def _get_next_ordinal(objects):
    """ 
        Helper: Retrieve the next ordinal in sequence for the given queryset identifying an ordered set of objects.
        This could be subject to a concurrency issue if two objects are saved simultaneously!
        Ideally, Django would allow us to simply use an auto-incrementing field for this... :-P

        # doctest
            >>> cs = CreditSet.objects.create(release_date="2010-01-01")
            >>> cat = Category.objects.create(creditset=cs, title="Cat 1", abbreviation='Test', max_point_value=1, description="this is a test")
            >>> Category.objects.get(pk=1).ordinal
            0
            >>> cat = Category.objects.create(creditset=cs, title="Cat 2", abbreviation='Test', max_point_value=1, description="this is a test")
            >>> Category.objects.get(pk=2).ordinal
            1
            >>> _get_next_ordinal(cat.creditset.category_set.all())
            2
            >>> _get_next_ordinal(cat.subcategory_set.all())
            0
    """
    ordinal = 0
    list = objects.order_by('-ordinal')
    if (list.count() > 0):
        last = list[0]
        ordinal = last.ordinal + 1
    return ordinal

class CreditSet(models.Model):
    version = models.CharField(max_length=5, unique=True)
    release_date = models.DateField()
    tier_2_points = models.FloatField()
    
    class Meta:
        ordering = ('release_date',)
    
    def __unicode__(self):
        return smart_unicode("v%s" % self.version, encoding='utf-8', strings_only=False, errors='strict')
        
    def get_edit_url(self):
        return "/dashboard/credit-editor/%d/" % self.id
        
    def get_submit_url(self):
        return "/dashboard/submissions/"
        
    def get_parent(self):
        """ Returns the parent element for crumbs """
        return None
    
    @classmethod
    def get_latest_creditset(cls):
        """
            Returns the latest creditset (usually the one currently open for registration)
        """
        try:
            return CreditSet.objects.order_by('-release_date')[0]
        except:
            return None
    
class Category(models.Model):
    creditset = models.ForeignKey(CreditSet)
    title = models.CharField(max_length=64)
    abbreviation = models.CharField(max_length=6,help_text='Typically a 2 character code for the category. e.g., ER for Education & Research') # TODO validation
    ordinal = models.SmallIntegerField(default=-1)
    max_point_value = models.IntegerField(default=0)
    description = models.TextField()
    
    class Meta:
        ordering = ('ordinal',)
        verbose_name_plural = "Categories"
    
    def __unicode__(self):
        return smart_unicode(self.title, encoding='utf-8', strings_only=False, errors='strict')
        
    def __cmp__(self, other):
        """ Used for ordering by ordinal """
        return cmp(self.ordinal, other.ordinal)
        
    def get_edit_url(self):
        return "%s%d/" % (self.creditset.get_edit_url(), self.id)

    def get_submit_url(self):
        return "/dashboard/submissions/%d/" % (self.id)
        
    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.creditset

    def has_dependents(self):
        """ Return true if this Category has dependent objects lower in the credit hierarchy """
        return self.subcategory_set.all().count() > 0
    
    def get_dependents(self):
        """ Returns a list of dictionaries (name, queryset) for each set of objects directly dependent on this Category """
        return [ {'name':'Subcategories', 'queryset':self.subcategory_set.all()} ]
    
    def num_submissions(self):
        """ Return the number of credit submissions started for this category """
        from stars.apps.submissions.models import get_active_submissions
        return get_active_submissions(category=self).count()
    
    @transaction.commit_on_success
    def update_ordering(self):
        """ 
            Updates all the credit numbers for credits in this category.
            Credits must be re-numbered whenever a sub-category or credit is Added, Deleted, or Re-ordered.
            Careful not to re-order more than once in these cases: 
              (1) e.g., when a sub-category is deleted and thus goes on to delete all credits
              (2) e.g., when a credit is saved, causes a re-number, which in turn saves the credits, ... 
             Returns True if the ordering was changed, false otherwise.
        """
        order_changed = False
        count = 1
        for sub in self.subcategory_set.all():
            for credit in sub.credit_set.all().order_by('ordinal').filter(type='t1'):
                if credit.number != count:
                    credit.number = count
                    credit.save()
                    order_changed = True
                count += 1
            t2_count = 1
            for credit in sub.credit_set.all().order_by('ordinal').filter(type='t2'):
                if credit.number != t2_count:
                    credit.number = t2_count
                    credit.save()
                    order_changed = True
                t2_count += 1
        return order_changed
            
    def save(self, *args, **kwargs):
        if self.ordinal == -1 :
            self.ordinal = _get_next_ordinal(self.creditset.category_set.all())
        super(Category, self).save(*args, **kwargs)
    
    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sdelete/" % self.get_edit_url()

class Subcategory(models.Model):    
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=64)
    ordinal = models.SmallIntegerField(default=-1)
    max_point_value = models.IntegerField(default=0)
    description = models.TextField()
    
    class Meta:
        ordering = ('category', 'ordinal',)
        verbose_name_plural = "Subcategories"
    
    def __unicode__(self):
        return smart_unicode(self.title, encoding='utf-8', strings_only=False, errors='strict')
        
    def __cmp__(self, other):
        """ Used for ordering by ordinal """
        return cmp(self.ordinal, other.ordinal)
        
    def get_edit_url(self):
        return "%s%d/" % (self.category.get_edit_url(), self.id)
    
    def get_submit_url(self):
        return "%s%d/" % (self.category.get_submit_url(), self.id)
        
    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.category
        
    def get_tier1_credits(self):
        return self.credit_set.filter(type='t1')
        
    def get_tier2_credits(self):
        return self.credit_set.filter(type='t2')

    def has_dependents(self):
        """ Return true if this Subcategory has dependent objects lower in the credit hierarchy """
        return self.credit_set.all().count() > 0

    def get_dependents(self):
        """ Returns a list of dictionaries (name, queryset) for each set of objects directly dependent on this Subcategory """
        return [ {'name':'Credits', 'queryset':self.credit_set.all()} ]

    def num_submissions(self):
        """ Return the number of credit submissions started for this subcategory """
        from stars.apps.submissions.models import get_active_submissions
        return get_active_submissions(subcategory=self).count()
        
    def update_ordering(self):
        """ 
            Updates all the credit numbers for credits in this category. 
            Returns True if the ordering was changed, false otherwise.
        """
        return self.category.update_ordering()
        
    def delete_and_update(self):
        """ Delete this sub-category and ensure category gets notified. """
        category = self.category
        self.delete()
        category.update_ordering()
        
    def save(self, *args, **kwargs):
        if self.ordinal == -1 :
            self.ordinal = _get_next_ordinal(self.category.subcategory_set.all())
        super(Subcategory, self).save(*args, **kwargs)

    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sdelete/" % self.get_edit_url()

    
CREDIT_TYPE_CHOICES = (
    ('t1', "Tier 1"),
    ('t2', "Tier 2"),
    )
    
class Credit(models.Model):
    subcategory = models.ForeignKey(Subcategory)
    title = models.CharField(max_length=64)
    ordinal = models.SmallIntegerField(help_text='The order of this credit within sub-category.', default=-1)
    number = models.SmallIntegerField(help_text='The number of this credit within the main category. EX: "ER Credit 1"',default=-1)
    point_value = models.FloatField(help_text='The maximum points awarded for this credit.')
    formula = models.TextField('Points Calculation Formula', blank=True, null=True, default="points = 0", help_text='Formula to compute credit points from values of the reporting fields')
    validation_rules = models.TextField('Custom Validation', blank=True, null=True, help_text='A Python script that provides custom validation for this credit.')
    type = models.CharField(max_length=2, choices=CREDIT_TYPE_CHOICES)
    criteria = models.TextField()
    applicability = models.TextField(blank=True, null=True)
    scoring = models.TextField()
    measurement = models.TextField(blank=True, null=True)
    staff_notes = models.TextField('AASHE Staff Notes', blank=True, null=True)
    
    class Meta:
        ordering = ('ordinal',)
    
    def __unicode__(self):
        return smart_unicode(self.title, encoding='utf-8', strings_only=False, errors='strict')

    def __str__(self):  # For DEBUG -  comment out __unicode__ method
        return "#%d: %s (%d)" % (self.number, self.title, self.ordinal)
        
    def __cmp__(self, other):
        """ Used for ordering by ordinal """
        return cmp(self.ordinal, other.ordinal)
        
    def get_edit_url(self):
        return "%s%d/" % (self.subcategory.get_edit_url(), self.id)
        
    def get_submit_url(self):
        return "%s%d/" % (self.subcategory.get_submit_url(), self.id)
        
    def get_identifier(self):
        """ Returns the indentifying string for the credit ex: 'ER Credit 10' """
        if self.type == 't2':
            return "Tier2-%d" % self.number
        return "%s-%s" % (self.subcategory.category.abbreviation, self.number)
        
    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.subcategory
        
    def has_dependents(self):
        """ Return true if this Subcategory has dependent objects lower in the credit hierarchy """
        return self.documentationfield_set.all().count() > 0 or self.applicabilityreason_set.all().count() > 0

    def get_dependents(self):
        """ Returns a list of dictionaries (name, queryset) for each set of objects directly dependent on this Subcategory """
        from stars.apps.submissions.models import CreditTestSubmission
        return [ {'name':'Reporting Fields', 'queryset':self.documentationfield_set.all()},
                 {'name':'Applicability Reasons', 'queryset':self.applicabilityreason_set.all()},
                 {'name':'Formula Test Cases', 'queryset':CreditTestSubmission.objects.filter(credit=self)},
               ]

    def num_submissions(self):
        """ Return the number of credit submissions started for this category """
        from stars.apps.submissions.models import get_active_submissions
        return get_active_submissions(credit=self).count()
        
    def delete_and_update(self):
        """ Delete this credit and ensure sub-category gets notified. """
        subcategory = self.subcategory
        self.delete()
        subcategory.update_ordering()

    def save(self, *args, **kwargs):
        if self.ordinal == -1 :
            self.ordinal = _get_next_ordinal(self.subcategory.credit_set.all())
        # Set the defaults for t2 credits
        if self.type == 't2':
            t2_points = self.subcategory.category.creditset.tier_2_points
            self.point_value = t2_points
            self.scoring = u"%.2f points available." % t2_points
            self.formula = u"""if A == True:
    points = %.2f
else:
    points = 0""" % t2_points
        super(Credit, self).save(*args, **kwargs)

    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sdelete/" % self.get_edit_url()

    def get_formula_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sformula/" % self.get_edit_url()

    def get_next_field_identifier(self):
        """ 
            Helper: return the next identifier for a new documentation field for this credit 
            @return a unique two-character identifier, of form "AB"
        """
        fields = self.documentationfield_set.all().order_by('-identifier')[:1]
        lastIdent = ''
        if (fields):
            lastIdent = fields[0].identifier

        return _next_identifier(lastIdent)
    
    def execute_formula(self, submission):
        """ 
            Execute the formula for this credit for the given submission data
            @param submission: a CreditSubmission for this credit containing data values to evaluate formula against
            @return: (Boolean, String/None, Exception/None, Type) = (success, message, exception, points)
                - success: True if formula executed without exception
                - message: suitable to report the result to the user or None
                - exception: if not success or None
                - points: the results of the formula execution (may not be numeric!!)
        """
        # get the key that relates field identifiers to their values
        field_key = submission.get_submission_field_key()
        points = 0;
        try:
            if (self.formula):
                # exec formula in restricted namespace
                globals = {}  # __builtins__ gets added automatically
                locals = {"points":points}
                locals.update(field_key)
                exec self.formula in globals, locals
                points = locals['points']
        except AssertionError, e:  # Assertions may be used in formula for extra validation - assume assertion text is intended for user
            return(False, "%s"%e, e, points)
        except Exception, e:
            watchdog.log("Credit", "Formula Exception: %s"%e, watchdog.ERROR)
            return(False, "There was an error processing this credit. AASHE has noted the error and will work to resolve the issue.", e, points)
        return (True, "Formula executed successfully", None, points)
        
    def execute_validation_rules(self, submission_form):
        """ 
            Execute the validation rules for this credit for the given submission data
            @param submission_form: a CreditSubmissionForm for this credit containing data values to validate
            @return:
                - errors: a dictionary of errors, using the field's identifier as the key for each error 
                    - may contain an 'top' key for credit-wide errors; 
                    - will be empty if validation passed without error
        """
        # get the key that relates field identifiers to their values
        field_key = submission_form.get_submission_field_key()
        errors={}
        try:
            if (self.validation_rules):
                # exec the validation in restricted namespace
                globals = {}  # __builtins__ gets added automatically
                locals = {"errors":errors,}
                locals.update(field_key)
                exec self.validation_rules in globals, locals
                errors = locals['errors']
        except AssertionError, e:  # Assertions may be used in validation to ensure conditions for validation are met - assume any assertion text is intended for user
            if str(e):
                errors['top'] ="%s"%e
        except Exception, e:
            watchdog.log("Credit", "Validation Exception: %s"%e, watchdog.ERROR)
            errors['top'] = "There was an error processing this credit. AASHE has noted the error and will work to resolve the issue." 
        return errors

    def compile_formula(self):
        """ See global compile_formula function... """
        return compile_formula(self.formula)

    def compile_validation_rules(self):
        """ See global compile_formula function... """
        return compile_formula(self.validation_rules, "Validation Rules")

def compile_formula(formula, label='Formula'):
    """ 
        Global function provided so that field validation has access to wrapped compile functionality
        Attempt to compile a formula.
        @return (boolean, message)
            - If the formula is None or compiles successfully, return true
            - If the formula fails to compile, return false

        #doctest:
            >>> compile_formula("")
            (True, 'No Formula specified')
            >>> compile_formula("A=3\\n points = 2 if A>3 else 1")
            (False, 'Formula did not compile: unexpected indent (formula, line 2)')
            >>> compile_formula("A=3\\npoints = 2 if A>3 else 1")
            (True, 'Formula compiled - code is valid.')
    """  
    if (formula) :
        try:
            compile(formula, label, 'exec')
            return (True, "%s compiled - code is valid."%label)
        except Exception, e:
            return (False, "%s did not compile: %s" %(label, e))          
    else:
        return (True, "No %s specified"%label)

def _next_identifier(identifier):
    """ 
        Helper: takes a simple all upper-case alpha identifier and 
        @returns the next identifier in the series:

        #doctest
            >>> _next_identifier("")
            'A'
            >>> _next_identifier("A")
            'B'
            >>> _next_identifier("Z")
            'AA'
            >>> _next_identifier("AZ")
            'BA'
            >>> _next_identifier("ZZ")
            'AAA'
    """     
    if not identifier:
        return 'A'
    prefix = identifier[0:-1]
    suffix = identifier[-1:]
    if suffix == 'Z':
        prefix = _next_identifier(prefix)
        suffix = 'A'
    else:
        suffix = chr(ord(suffix)+1)
    return "%s%s"%(prefix,suffix)     
        
class ApplicabilityReason(models.Model):
    """
        Models reasons why a particular credit might be allowed to be considered not-applicable
    """
    credit = models.ForeignKey(Credit)
    reason = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.reason
    
    def get_absolute_url(self):
        return "%sapplicability/" % self.credit.get_edit_url()

    def get_edit_url(self):
        return "%s%d/" % (self.get_absolute_url(), self.id)
        
    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sdelete/" % self.get_edit_url()
    
    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.credit
    
    def num_submissions(self):
        """ Return the number of credit submissions where this ApplicabilityReason was cited """
        from stars.apps.submissions.models import get_na_submissions
        return get_na_submissions(applicability_reason=self).count()
        
    def delete(self):
        """ Override delete to update any submissions that reference this reason - otherwise the whole submission would be deleted! """
        from stars.apps.submissions.models import get_na_submissions
        submissions = get_na_submissions(applicability_reason=self)
        for submission in submissions:
            submission.applicability_reason = None
            submission.mark_as_in_progress()
            submission.save()
        super(ApplicabilityReason, self).delete()
        

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
#    ('multiple_upload', 'multiple upload'),
)

REQUIRED_TYPES = (
    ('opt', "optional"),
    ('cond', "conditionally required"),
    ('req', 'required'),
    )

class Unit(models.Model):
    name = models.CharField(max_length=32)
    
    class Meta:
        ordering = ('name',)
        
    def __unicode__(self):
        return smart_unicode(self.name, encoding='utf-8', strings_only=False, errors='strict')

class DocumentationField(models.Model):
    credit = models.ForeignKey(Credit)
    title = models.CharField("Promt/Question", max_length=255)
    type = models.CharField(max_length=16, choices=DOCUMENTATION_FIELD_TYPES)
    last_choice_is_other = models.BooleanField(default=False, help_text='If selected, the last choice provides a box to enter a user-defined choice')
    min_range = models.IntegerField(help_text='Numeric: miniumum integer value, Date: earliest year.', blank=True, null=True)
    max_range = models.IntegerField(help_text='Text: max character count, LongText: max word count, Numeric: max integer value, Date: latest year.', blank=True, null=True)
    units = models.ForeignKey(Unit, null=True, blank=True)
    inline_help_text = models.TextField(null=True, blank=True)
    tooltip_help_text = models.TextField(null=True, blank=True)
    ordinal = models.SmallIntegerField(default=-1)
    required = models.CharField(max_length=8, choices=REQUIRED_TYPES, default='req', help_text='If a field is conditionally required it is important to note that in the help-text and to define a custom validation rule.')
    is_confidential = models.BooleanField()
    identifier = models.CharField(max_length=2) # editable=False) # Field identifier for the Formula editor - auto-generated.
    
    class Meta:
        ordering = ('ordinal',)

    def save(self, *args, **kwargs):
        """ Override model.Model save() method to assign identifier and ordinal """
        if not self.identifier:
            self.identifier = self.credit.get_next_field_identifier()
        if self.ordinal == -1 :
            self.ordinal = _get_next_ordinal(self.credit.documentationfield_set.all())
        super(DocumentationField, self).save(*args, **kwargs)
         
    def __unicode__(self):
        """ Limit the length of the text representation to 50 characters """
        label = smart_unicode(self.title, encoding='utf-8', strings_only=False, errors='strict')
        if len(label) > 50:
            l, b, r = label[0:50].rpartition(' ')
            if not l:
                l = label[0:50]
            label = "%s ..."%l 
        return label
    
    def __cmp__(self, other):
        """ Used for ordering by ordinal """
        return cmp(self.ordinal, other.ordinal)
    
    def get_edit_url(self):
        return "%s%d/" % (self.credit.get_edit_url(), self.id)
        
    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.credit
    
    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sdelete/" % self.get_edit_url()
    
    def is_required(self):
        """ Return true if this field is required to complete a submission """
        return self.required == 'req'
    
    def is_conditionally_required(self):
        """ Return true if this field is conditionally required """
        return self.required == 'cond'

    def is_single_choice(self):
        """ Return true if this field is a single choice """
        return self.type == 'choice'
    
    def is_multi_choice(self):
        """ Return true if this field is a multi-choice """
        return self.type == 'multichoice'
    
    def is_choice(self):
        """ Return true if this field is a choice """
        return self.type.endswith('choice')
    
    def has_other_choice(self):
        """ Return True iff this field specifies a choice with other type selection """
        return self.last_choice_is_other
               
    def can_have_min_max(self):
        """ Return True iff the min / max options apply to this field. """
        return self.type in ('text', 'long_text', 'numeric', 'date') and not self.is_choice()

    def can_have_units(self):
        """ Return True iff the units option apply to this field. """
        return self.type in ('text', 'long_text', 'numeric') or self.is_choice()

    def get_units(self):
        """ Return the units associated with this field or None """
        return self.units if self.can_have_units() else None
               
    def num_submissions(self):
        """ Return the number of credit submissions where this ApplicabilityReason was cited """
        from stars.apps.submissions.models import get_active_field_submissions
        return get_active_field_submissions(self).count()


class Choice(models.Model):
    """
        A choice for a documentation field
        Stores both 'official' (bonafide) choices defined by STARS and user-defined choices. 
    """
    documentation_field = models.ForeignKey(DocumentationField)
    choice = models.CharField("Choice", max_length=255)
    ordinal = models.SmallIntegerField(default=-1)
    is_bonafide = models.BooleanField(default=True)  # 'bonafide' choices are defined by STARS staff, other choices are user=defined
    
    class Meta:
        ordering = ('ordinal',)

    def __unicode__(self):
        return self.choice

    def __cmp__(self, other):
        """ Used for ordering by ordinal """
        return cmp(self.ordinal, other.ordinal)
    
    def get_absolute_url(self):
        return "%schoice/" % self.documentation_field.get_edit_url()

    def get_edit_url(self):
        return "%s%d/" % (self.get_absolute_url(), self.id)
        
    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sdelete/" % self.get_edit_url()
    
    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.documentation_field
    
    def save(self, *args, **kwargs):
        if self.ordinal is None or self.ordinal == -1 :
            self.ordinal = _get_next_ordinal(self.documentation_field.choice_set.all())
        super(Choice, self).save(*args, **kwargs)

    def num_submissions(self):
        """ Return the number of credit submissions where this Choice was cited """
        from stars.apps.submissions.models import get_active_field_submissions
        return get_active_field_submissions(choice=self).count()