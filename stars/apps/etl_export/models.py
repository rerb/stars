from datetime import datetime, timedelta

from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db.models import Max

from stars.apps.institutions.models import RATINGS_PER_SUBSCRIPTION
from stars.apps import submissions
from stars.apps import institutions

from stars.apps.etl_export.mixins import ETLCompareMixin

"""
    Notes
     - aashe_id can be "-1"
"""


class Institution(ETLCompareMixin):
    """
        This model houses all the required fields for the
        Salesforce Extract Transform and Load operation for
        Institutions
    """
    aashe_id = models.IntegerField()

    liaison_first_name = models.CharField(max_length=32)
    liaison_middle_name = models.CharField(max_length=32, blank=True, null=True)
    liaison_last_name = models.CharField(max_length=32)
    liaison_title = models.CharField(max_length=255)
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

    current_submission_id = models.IntegerField(blank=True, null=True)
    current_subscription_id = models.IntegerField(blank=True, null=True)
    rated_submission_id = models.IntegerField(blank=True, null=True)
    current_stars_version = models.CharField(max_length=5)
    last_submission_date = models.DateField(blank=True, null=True)
    submission_due_date = models.DateField(blank=True, null=True)
    is_published = models.BooleanField()

    # for ETLCompareMixin
    etl_source_class = institutions.models.Institution

    def __str__(self):
        return "%d" % self.aashe_id

    def populate(self, institution):
        """
            An ETL object has to be initialized with an object to populate from
        """
        if institution.id == 54:
            pass
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
            self.current_stars_version = institution.current_submission.creditset.version

        self.current_subscription = None
        if institution.current_subscription:
            self.current_subscription_id = institution.current_subscription.id

        self.rated_submission = None
        if institution.rated_submission:
            self.rated_submission_id = institution.rated_submission.id
            self.last_submission_date = institution.rated_submission.date_submitted


class Subscription(ETLCompareMixin):
    """
        A mirror of the institutions.Subscription model
    """

    aashe_id = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    ratings_allocated = models.SmallIntegerField(default=RATINGS_PER_SUBSCRIPTION)
    ratings_used = models.IntegerField(default=0)
    price = models.FloatField()
    amount_due = models.FloatField()
    reason = models.CharField(max_length='16', blank=True, null=True)
    paid_in_full = models.BooleanField(default=False)
    close_date = models.DateField(blank=True, null=True)

    # for ETLCompareMixin
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
        self.amount_due = sub.amount_due
        self.reason = sub.reason
        self.paid_in_full = sub.paid_in_full
        self.price = 0

        last_payment_date = sub.subscriptionpayment_set.aggregate(Max('date'))['date__max']

        if self.paid_in_full:
            self.price = 0
            self.close_date = last_payment_date
            if not last_payment_date:
                # just in case there were no payments for some reason
                self.close_date = sub.start_date
        else:
            self.price = self.amount_due
            self.close_date = self.start_date + timedelta(days=90)

        for p in sub.subscriptionpayment_set.all():
            self.price += p.amount


class SubscriptionPayment(ETLCompareMixin):
    """
        A mirror of the institutions.SubscriptionPayment model
    """

    aashe_id = models.IntegerField()
    subscription_id = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField()
    amount = models.FloatField()
    user = models.EmailField()
    method = models.CharField(max_length='8')
    confirmation = models.CharField(max_length='16', blank=True, null=True)

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


class SubmissionSet(ETLCompareMixin):
    """
        A mirrored version of the submissions.SubmissionSet model
        for export to SF
    """
    
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

        self.is_active = ss.institution.get_active_submission() == ss


class Boundary(ETLCompareMixin):
    """
        A mirrored version of the submissions.Boundary model
        for export to SF
    """

    aashe_id = models.IntegerField()
    submissionset = models.IntegerField(blank=True, null=True)

    # Characteristics
    fte_students = models.IntegerField("Full-time Equivalent Enrollment", blank=True, null=True)
    undergrad_count = models.IntegerField("Number of Undergraduate Students", blank=True, null=True)
    graduate_count = models.IntegerField("Number of Graduate Students", blank=True, null=True)
    fte_employmees = models.IntegerField("Full-time Equivalent Employees", blank=True, null=True)
    institution_type = models.CharField(max_length=32, blank=True, null=True)
    institutional_control = models.CharField(max_length=32, blank=True, null=True)
    endowment_size = models.BigIntegerField(blank=True, null=True)
    student_residential_percent = models.FloatField('Percentage of students that are Residential', blank=True, null=True)
    student_ftc_percent = models.FloatField('Percentage of students that are Full-time commuter', blank=True, null=True)
    student_ptc_percent = models.FloatField('Percentage of students that are Part-time commuter', blank=True, null=True)
    student_online_percent = models.FloatField('Percentage of students that are On-line only', blank=True, null=True)
    gsf_building_space = models.FloatField("Gross square feet of building space", blank=True, null=True)
    gsf_lab_space = models.FloatField("Gross square feet of laboratory space", help_text='Scientific research labs and other high performance facilities eligible for <a href="http://www.labs21century.gov/index.htm" target="_blank">Labs21 Environmental Performance Criteria</a> (EPC).', blank=True, null=True)
    cultivated_grounds_acres = models.FloatField("Acres of cultivated grounds", help_text="Areas that are landscaped, planted, and maintained (including athletic fields). If less than 5 acres, data not necessary.", blank=True, null=True)
    undeveloped_land_acres = models.FloatField("Acres of undeveloped land", help_text="Areas without any buildings or development. If less than 5 acres, data not necessary", blank=True, null=True)
    climate_region = models.CharField(max_length=32, help_text="See the <a href='http://www1.eere.energy.gov/buildings/building_america/climate_zones.html'>USDOE</a> site and <a href='http://www.ashrae.org/File%20Library/docLib/Public/20081111_cztables.pdf'>ASHRAE</a>  (international) for more information.", blank=True, null=True)

    # Features
    ag_school_present = models.BooleanField("Agricultural school is present")
    ag_school_included = models.BooleanField("Agricultural school is included in submission")
    ag_school_details = models.TextField("Reason for Exclusion", blank=True, null=True)
    med_school_present = models.BooleanField("Medical school is present")
    med_school_included = models.BooleanField("Medical school is included in submission")
    med_school_details = models.TextField("Reason for Exclusion", blank=True, null=True)
    pharm_school_present = models.BooleanField("Pharmacy school is present")
    pharm_school_included = models.BooleanField("Pharmacy school is included in submission")
    pharm_school_details = models.TextField("Reason for Exclusion", blank=True, null=True)
    pub_health_school_present = models.BooleanField("Public health school is present")
    pub_health_school_included = models.BooleanField("Public health school is included in submission")
    pub_health_school_details = models.TextField("Reason for Exclusion", blank=True, null=True)
    vet_school_present = models.BooleanField("Veterinary school is present")
    vet_school_included = models.BooleanField(" Veterinary school is included in submission")
    vet_school_details = models.TextField("Reason for Exclusion", blank=True, null=True)
    sat_campus_present = models.BooleanField("Satellite campuses are present")
    sat_campus_included = models.BooleanField("Satellite campuses are included in submission")
    sat_campus_details = models.TextField("Reason for Exclusion", blank=True, null=True)
    hospital_present = models.BooleanField("Hospital is present")
    hospital_included = models.BooleanField("Hospital is included in submission")
    hospital_details = models.TextField("Reason for Exclusion", blank=True, null=True)
    farm_present = models.BooleanField("Farm is present", help_text='Larger than 5 acres')
    farm_included = models.BooleanField("Farm is included in submission")
    farm_acres = models.FloatField("Number of acres", blank=True, null=True)
    farm_details = models.TextField("Reason for Exclusion", blank=True, null=True)
    agr_exp_present = models.BooleanField("Agricultural experiment station is present", help_text='Larger than 5 acres')
    agr_exp_included = models.BooleanField("Agricultural experiment station is included in submission")
    agr_exp_acres = models.IntegerField("Number of acres", blank=True, null=True)
    agr_exp_details = models.TextField("Reason for Exclusion", blank=True, null=True)

    additional_details = models.TextField(blank=True, null=True)

    # for ETLCompareMixin
    etl_populate_exclude_fields = ['id', 'change_date', 'aashe_id', 'climate_region', 'submissionset']
    etl_source_class = submissions.models.Boundary

    def populate(self, b):
        """
            An ETL object has to be initialized with an object to populate from
        """

        self.populate_all(b)

        self.id = b.id
        if b.climate_region:
            self.climate_region = b.climate_region.name
        self.submissionset_id = b.submissionset_id
        self.aashe_id = b.submissionset.institution.aashe_id
        if not self.aashe_id:
            self.aashe_id = -1
