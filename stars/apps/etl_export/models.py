from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField

from stars.apps.institutions.models import RATINGS_PER_SUBSCRIPTION
from stars.apps import submissions
from stars.apps import institutions

from stars.apps.credits.models import Rating
from stars.apps.etl_export.mixins import ETLCompareMixin

from datetime import timedelta, datetime

"""
    Notes
     - will add boundary later
     - aashe_id can be "-1"
"""
        
class Institution(models.Model, ETLCompareMixin):
    """
        This model houses all the required fields for the
        Salesforce Extract Transform and Load operation for
        Institutions
    """
    aashe_id = models.IntegerField()
    change_date = models.DateTimeField(auto_now=True)
    
    liaison_first_name = models.CharField(max_length=32)
    liaison_middle_name = models.CharField(max_length=32, blank=True, null=True)
    liaison_last_name = models.CharField(max_length=32)
    liaison_title = models.CharField(max_length=64)
    liaison_department = models.CharField(max_length=64)
    liaison_phone = PhoneNumberField()
    liaison_email = models.EmailField()
    
    charter_participant = models.BooleanField()
    international = models.BooleanField(default=False)
    
    is_participant = models.BooleanField()
    current_rating = models.CharField(max_length=16, null=True, blank=True)
    rating_expires = models.DateField(blank=True, null=True)
    registration_date = models.DateField(blank=True, null=True)
    last_submission_date = models.DateField(blank=True, null=True)
    submission_due_date = models.DateField(blank=True, null=True)
    
    current_submission = models.ForeignKey("SubmissionSet", blank=True, null=True, related_name="current")
    current_subscription = models.ForeignKey("Subscription", blank=True, null=True, related_name='current')
    rated_submission = models.ForeignKey("SubmissionSet", blank=True, null=True, related_name='rated')
    current_stars_version = models.CharField(max_length=5)
    rating_valid_until = models.DateField(blank=True, null=True)
    registration_date = models.DateField(blank=True, null=True)
    last_submission_date = models.DateField(blank=True, null=True)
    submission_due_date = models.DateField(blank=True, null=True)
    is_published = models.BooleanField()

    # for ETLCompareMixin
    etl_exclude_fields = ['change_date',]
    etl_source_class = institutions.models.Institution

    def __str__(self):
        return "%d" % self.aashe_id

    def populate(self, institution):
        """
            An ETL object has to be initialized with an object to populate from
        """

        self.id = institution.id
        self.aashe_id = institution.aashe_id
        if not self.aashe_id:
            self.aashe_id = -1
        self.change_date = datetime.now()
        
        custom_mappings = (
                    ("liaison_first_name", "contact_first_name"),
                    ("liaison_middle_name", "contact_middle_name"),
                    ("liaison_last_name", "contact_last_name"),
                    ("liaison_title", "contact_title"),
                    ('liaison_department', 'contact')
                    )

        # Grab necessary data
        self.liaison_first_name = institution.contact_first_name
        self.liaison_middle_name = institution.contact_middle_name
        self.liaison_last_name = institution.contact_last_name
        self.liaison_title = institution.contact_title
        self.liaison_department = institution.contact_department
        self.liaison_phone = institution.contact_phone
        self.liaison_email = institution.contact_email
        
        self.charter_participant = institution.charter_participant
        self.international = institution.international
        
        self.is_participant = institution.is_participant
        
        self.current_rating = None
        if institution.current_rating:
            self.current_rating = institution.current_rating.name
            
        self.rating_expires = institution.rating_expires
        
        self.current_submission = None
        if institution.current_submission:
            self.current_submission_id = institution.current_submission.id
        
        institution.current_subscription = None
        if institution.current_subscription:
            self.current_subscription_id = institution.current_subscription.id
        
        self.rated_submission = None
        if institution.rated_submission:
            self.rated_submission_id = institution.rated_submission.id

class Subscription(models.Model, ETLCompareMixin):
    """
        A mirror of the institutions.Subscription model
    """
    
    change_date = models.DateTimeField(auto_now=True)
    aashe_id = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    ratings_allocated = models.SmallIntegerField(default=RATINGS_PER_SUBSCRIPTION)
    ratings_used = models.IntegerField(default=0)
    price = models.FloatField()
    reason = models.CharField(max_length='16', blank=True, null=True)
    paid_in_full = models.BooleanField(default=False)
    
    # for ETLCompareMixin
    etl_exclude_fields = ['change_date',]
    etl_source_class = institutions.models.Subscription
    
    def populate(self, sub):
        """
            Populate this object from the original subscription object
        """
        self.id = sub.id
        self.aashe_id = sub.institution.aashe_id
        if not self.aashe_id:
            self.aashe_id = -1
        self.change_date = datetime.now()
        
        self.start_date = sub.start_date
        self.end_date = sub.end_date
        self.ratings_allocated = sub.ratings_allocated
        self.ratings_used = sub.ratings_used
        self.price = sub.amount_due
        self.reason = sub.reason
        self.paid_in_ful = sub.paid_in_full

class SubscriptionPayment(models.Model, ETLCompareMixin):
    """
        A mirror of the institutions.SubscriptionPayment model
    """
    
    change_date = models.DateTimeField(auto_now=True)
    aashe_id = models.IntegerField()
    subscription = models.ForeignKey("Subscription")
    date = models.DateTimeField()
    amount = models.FloatField()
    user = models.EmailField()
    method = models.CharField(max_length='8')
    confirmation = models.CharField(max_length='16', blank=True, null=True)
    
    etl_exclude_fields = ['change_date',]
    etl_source_class = institutions.models.SubscriptionPayment
    
    def populate(self, p):
        """
            Populate this object from the original payment object
        """
        self.id = p.id
        self.aashe_id = p.subscription.institution.aashe_id
        if not self.aashe_id:
            self.aashe_id = -1
        self.change_date = datetime.now()
        
        self.subscription_id = p.subscription_id
        self.date = p.date
        self.amount = p.amount
        self.user = p.user.email
        self.method = p.method
        self.confirmation = p.confirmation
        
class SubmissionSet(models.Model, ETLCompareMixin):
    """
        A mirrored version of the submissions.SubmissionSet model
        for export to SF
    """
    
    change_date = models.DateTimeField(auto_now=True)
    version = models.CharField(max_length=8)
    aashe_id = models.IntegerField()
    date_registered = models.DateField()
    date_submitted = models.DateField(blank=True, null=True)
    registering_user = models.EmailField()
    submitting_user = models.EmailField(blank=True, null=True)
    rating = models.CharField(max_length=16)
    status = models.CharField(max_length=8, choices=submissions.models.SUBMISSION_STATUS_CHOICES)
    reporter_status = models.NullBooleanField()
    score = models.FloatField(blank=True, null=True)
    is_active = models.BooleanField()
    
    # for ETLCompareMixin
    etl_exclude_fields = ['change_date',]
    etl_source_class = submissions.models.SubmissionSet
    
    def populate(self, ss):
        """
            An ETL object has to be initialized with an object to populate from
        """
        
        self.id = ss.id
        self.version = ss.creditset.version
        self.aashe_id = ss.institution.aashe_id
        if not self.aashe_id:
            self.aashe_id = -1
        
        self.date_registered = ss.date_registered
        self.date_submitted = ss.date_submitted
        self.registering_user = ss.registering_user.email
        if ss.rating:
            self.rating = ss.rating.name
        self.status = ss.status
        self.reporter_status = ss.reporter_status
        self.score = ss.get_STARS_score()
