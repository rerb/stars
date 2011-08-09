from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField

from stars.apps.institutions.models import Institution
from stars.apps import submissions
from stars.apps import institutions
from stars.apps.credits.models import Rating
from stars.apps.etl_export.mixins import ETLCompareMixin

from datetime import timedelta, datetime

class ETL(models.Model):
    """
        NOTE: this is the old version of this model. The new version
        is now stored in Institution below
    
        This model houses all the required fields for the
        Salesforce Extract Transform and Load operation.
    """
    institution = models.ForeignKey(Institution, blank=True, null=True)
    aashe_id = models.IntegerField()
    change_date = models.DateTimeField(auto_now=True)
    participant_status = models.CharField(max_length=32, blank=True, null=True)
    current_rating = models.CharField(max_length=16, null=True, blank=True)
    rating_valid_until = models.DateField(blank=True, null=True)
    registration_date = models.DateField(blank=True, null=True)
    last_submission_date = models.DateField(blank=True, null=True)
    submission_due_date = models.DateField(blank=True, null=True)
    current_stars_version = models.CharField(max_length=5)
    liaison_first_name = models.CharField(max_length=32)
    liaison_middle_name = models.CharField(max_length=32, blank=True, null=True)
    liaison_last_name = models.CharField(max_length=32)
    liaison_title = models.CharField(max_length=64)
    liaison_department = models.CharField(max_length=64)
    liaison_phone = PhoneNumberField()
    liaison_email = models.EmailField()
    is_published = models.BooleanField()
    
    def __str__(self):
        return "%d" % self.aashe_id
        
class Institution(models.Model, ETLCompareMixin):
    """
        This model houses all the required fields for the
        Salesforce Extract Transform and Load operation for
        Institutions
    """
    aashe_id = models.IntegerField()
    change_date = models.DateTimeField(auto_now=True)
    participant_status = models.CharField(max_length=32, blank=True, null=True)
    current_rating = models.CharField(max_length=16, null=True, blank=True)
    rating_valid_until = models.DateField(blank=True, null=True)
    registration_date = models.DateField(blank=True, null=True)
    last_submission_date = models.DateField(blank=True, null=True)
    submission_due_date = models.DateField(blank=True, null=True)
    current_stars_version = models.CharField(max_length=5)
    liaison_first_name = models.CharField(max_length=32)
    liaison_middle_name = models.CharField(max_length=32, blank=True, null=True)
    liaison_last_name = models.CharField(max_length=32)
    liaison_title = models.CharField(max_length=64)
    liaison_department = models.CharField(max_length=64)
    liaison_phone = PhoneNumberField()
    liaison_email = models.EmailField()
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
        self.change_date = datetime.now()

        # Grab necessary data
        last_submission = institution.get_latest_submission(include_unrated=True)
        last_rated_submission = institution.get_latest_submission()
        active_submission = institution.get_active_submission()

        # Populate ETL object
        if last_submission:
            self.participant_status = last_submission.get_status_display()
            self.submission_due_date = last_submission.submission_deadline
            self.registration_date = last_submission.date_registered
        if last_rated_submission:
            self.current_rating = last_rated_submission.rating.name
            self.rating_valid_until = last_rated_submission.date_submitted + timedelta(days=365*3)
            self.last_submission_date = last_rated_submission.date_submitted
        if active_submission:
            self.current_stars_version = active_submission.creditset.version
        elif last_submission:
            self.current_stars_version = last_submission.creditset.version

        self.liaison_first_name = institution.contact_first_name
        self.liaison_middle_name = institution.contact_middle_name
        self.liaison_last_name = institution.contact_last_name
        self.liaison_title = institution.contact_title
        self.liaison_department = institution.contact_department
        self.liaison_phone = institution.contact_phone
        self.liaison_email = institution.contact_email

        self.is_published = institution.is_published()
        self.institution = institution

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
    date_reviewed = models.DateField(blank=True, null=True)
    submission_deadline = models.DateField()
    rating = models.CharField(max_length=16)
    status = models.CharField(max_length=8, choices=submissions.models.SUBMISSION_STATUS_CHOICES)
    reporter_status = models.NullBooleanField()
    score = models.FloatField(blank=True, null=True)
    
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
        self.date_registered = ss.date_registered
        self.date_submitted = ss.date_submitted
        self.date_reviewed = ss.date_reviewed
        self.submission_deadline = ss.submission_deadline
        if ss.rating:
            self.rating = ss.rating.name
        self.status = ss.status
        self.reporter_status = ss.reporter_status
        self.score = ss.get_STARS_score()

class Payment(models.Model, ETLCompareMixin):
    """
        A mirrored version of the submissions.Payment model
        for export to SF
    """
    
    change_date = models.DateTimeField(auto_now=True)
    submissionset = models.IntegerField()
    date = models.DateTimeField()
    amount = models.FloatField()
    user = models.EmailField()
    reason = models.CharField(max_length='8', choices=submissions.models.PAYMENT_REASON_CHOICES)
    type = models.CharField(max_length='8', choices=submissions.models.PAYMENT_TYPE_CHOICES)
    confirmation = models.CharField(max_length='16', blank=True, null=True, help_text='The CC confirmation code or check number')
    
    # for ETLCompareMixin
    etl_exclude_fields = ['change_date',]
    etl_source_class = submissions.models.Payment
    
    def populate(self, payment):
        """
            An ETL object has to be initialized with an object to populate from
        """
        self.id = payment.id
        self.submissionset = payment.submissionset.id
        self.date = payment.date
        self.amount = payment.amount
        self.user = payment.user.email
        self.reason = payment.reason
        self.type = payment.type
        self.confirmation = payment.confirmation