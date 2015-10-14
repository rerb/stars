import os
import re
import sys
from datetime import date, datetime, timedelta
from logging import getLogger

import numpy
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.localflavor.us.models import PhoneNumberField
from django.core import urlresolvers
from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models import Q

from stars.apps.credits.models import (ApplicabilityReason, Category, Choice,
                                       Credit, CreditSet, DocumentationField,
                                       Rating, Subcategory)
from stars.apps.institutions.models import ClimateZone, Institution
from stars.apps.notifications.models import EmailTemplate
from stars.apps.submissions.export.pdf import build_report_pdf


PENDING_SUBMISSION_STATUS = 'ps'
PROCESSSING_SUBMISSION_STATUS = 'pr'
RATED_SUBMISSION_STATUS = 'r'
FINALIZED_SUBMISSION_STATUS = 'f'

SUBMISSION_STATUS_CHOICES = (
    (PENDING_SUBMISSION_STATUS, 'Pending Submission'),
    (PROCESSSING_SUBMISSION_STATUS, 'Processing Submission'),
    (RATED_SUBMISSION_STATUS, 'Rated'),
    (FINALIZED_SUBMISSION_STATUS, 'Finalized'),
)

# Max # of extensions allowed per submission set
MAX_EXTENSIONS = 1

# Extension period
EXTENSION_PERIOD = timedelta(days=366/2)

# Rating valid for
RATING_VALID_PERIOD = timedelta(days=365 * 3)

# Institutions that registered before May 29th, but haven't paid are
# still published.
REGISTRATION_PUBLISH_DEADLINE = date(2010, 5, 29)

logger = getLogger('stars')


def upload_path_callback(instance, filename):
    """
        Dynamically alters the upload path based on the instance
    """
    path = instance.get_upload_path()
    path = "%s%s" % (path, filename)
    return path


class Flag(models.Model):
    """
        A flag that can be added by staff for a submission/credit/field
    """
    date = models.DateField(auto_now_add=True)
    description = models.TextField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey('content_type', 'object_id')

    def get_admin_url(self):
        return urlresolvers.reverse("admin:submissions_flag_change",
                                    args=[self.id])

    def __unicode__(self):
        return "%s" % self.target


class FlaggableModel():
    # flags = generic.GenericRelation(Flag, content_type_field='content_type',
    #                                 object_id_field='object_id')

    def get_flag_url(self):

        # return "%s/%d/flag/" % (self.credit_submission.get_scorecard_url(),
        #                         self.id)
        link = "%s?content_type=%s&object_id=%d" % (
            urlresolvers.reverse('admin:submissions_flag_add'),
            ContentType.objects.get_for_model(self).id,
            self.id
        )
        return link

    @property
    def flags(self):
        type = ContentType.objects.get_for_model(self)
        return Flag.objects.filter(content_type__pk=type.id, object_id=self.id)


class SubmissionManager(models.Manager):
    """
        Adds some custom query functionality to the SubmissionSet object
    """

    def published(self):
        """ Submissionsets that have been paid in full or unpaid before
        May 28th.
        """

        deadline = REGISTRATION_PUBLISH_DEADLINE
        qs1 = SubmissionSet.objects.filter(institution__enabled=True).filter(payment__isnull=False).filter(is_visible=True).filter(is_locked=False)
        qs2 = qs1.filter(
                (Q(payment__type='later') & Q(date_registered__lte=deadline)) | ~Q(payment__type='later'))
        return qs2.distinct()

    def get_rated(self):
        """ All submissionsets that have been rated (and are visible) """
        return SubmissionSet.objects.filter(
            institution__enabled=True).filter(
                is_visible=True).filter(
                    status='r')

    def get_snapshots(self, institution):
        return SubmissionSet.objects.filter(
            institution=institution).filter(
                status='f').order_by(
                    '-date_submitted')


class SubmissionSet(models.Model, FlaggableModel):
    """
        A creditset (ex: 1.0) that is being submitted
    """
    objects = SubmissionManager()
    creditset = models.ForeignKey(CreditSet)
    institution = models.ForeignKey(Institution)
    date_registered = models.DateField()
    date_submitted = models.DateField(blank=True, null=True)
    date_reviewed = models.DateField(blank=True, null=True)
    expired = models.BooleanField(default=False)
    registering_user = models.ForeignKey(
        User,
        related_name='registered_submissions')
    submitting_user = models.ForeignKey(User,
                                        related_name='submitted_submissions',
                                        blank=True,
                                        null=True)
    rating = models.ForeignKey(Rating, blank=True, null=True)
    status = models.CharField(max_length=8, choices=SUBMISSION_STATUS_CHOICES)
    submission_boundary = models.TextField(
        blank=True,
        null=True,
        help_text=("The following is an example institutional boundary: "
                   "This submission includes all of the the University's "
                   "main campus as well as the downtown satellite campus. "
                   "The University hospital and campus farm are excluded."))
    presidents_letter = models.FileField(
        "President's Letter",
        upload_to=upload_path_callback,
        blank=True,
        null=True,
        help_text=("AASHE requires that every submission be vouched "
                   "for by that institution's president. Please upload "
                   "a PDF or scan of a letter from your president."))
    reporter_status = models.BooleanField(
        help_text=("Check this box if you would like to be given "
                   "reporter status and not receive a STARS rating "
                   "from AASHE."))
    pdf_report = models.FileField(upload_to=upload_path_callback,
                                  blank=True,
                                  null=True)
    is_locked = models.BooleanField(default=False)
    is_visible = models.BooleanField(
        default=True,
        help_text=("Is this submission visible to the institution? "
                   "Often used with migrations."))
    score = models.FloatField(blank=True, null=True)
    migrated_from = models.ForeignKey('self', null=True, blank=True,
                                      related_name='+')
    date_created = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ("date_registered",)

    def __unicode__(self):
        return '%s (%s)' % (self.institution.name, self.creditset.version)

    def missed_deadline(self):
        return not self.institution.is_participant

    def get_upload_path(self):
        return 'secure/%d/submission-%d/' % (self.institution.id, self.id)

    def get_pdf(self, template=None, refresh=False):
        """
            Generates a PDF file from the report

            If the submission is rated the report can be saved in the
            model (unless refresh is set)
        """
        if self.status == 'r' and not refresh:
            if self.pdf_report:
                return self.pdf_report.file

        pdf_result = build_report_pdf(self, template)

        # Rated institutions can have their pdf saved
        if self.status == 'r':
            name = self.get_pdf_filename()
            f = InMemoryUploadedFile(pdf_result, "pdf", name, None,
                                     pdf_result.tell(), None)
            self.pdf_report.save(name, f)
            return self.pdf_report.file

        from django.core.files.temp import NamedTemporaryFile
        tempfile = NamedTemporaryFile(suffix='.pdf', delete=False)
        tempfile.write(pdf_result.getvalue())
        tempfile.close()
#         return pdf_result.getvalue()
        return tempfile.name

    def get_pdf_filename(self):
        return '%s.pdf' % self.institution.slug[:64]

    def is_enabled(self):
        if self.is_visible:
            for payment in self.payment_set.all():
                if payment.type == 'credit' or payment.type == 'check':
                    return True
        return False

    def was_submitted(self):
        """ Indicates if this set has been submitted for a rating. """
        return self.date_submitted != None

    def get_crumb_label(self):
        return str(self.creditset.version)

    def get_crumb_url(self):
        return self.get_manage_url()

    def get_admin_url(self):
        return "%ssubmissionsets/%d/" % (self.institution.get_admin_url(),
                                         self.id)

    def get_add_payment_url(self):
        return "%sadd-payment/" % self.get_admin_url()

    def get_manage_url(self):
        return urlresolvers.reverse(
            'submission-summary',
            kwargs={'institution_slug': self.institution.slug,
                    'submissionset': self.id})

    def get_submit_url(self):
        return urlresolvers.reverse(
            'submission-submit',
            kwargs={'institution_slug': self.institution.slug,
                    'submissionset': self.id})

    def get_scorecard_url(self):
        cache_key = "submission_%d_scorecard_url" % self.id
        url = cache.get(cache_key)
        if url:
            return url
        else:
            if self.date_submitted:
                url = '/institutions/%s/report/%s/' % (self.institution.slug,
                                                       self.date_submitted)
            else:
                url = '/institutions/%s/report/%s/' % (self.institution.slug,
                                                       self.id)
            cache.set(cache_key, url, 60 * 60 * 24)  # cache for 24 hours
            return url

    def get_parent(self):
        """ Used for building crumbs """
        return None

    def get_status(self):
        """ Returns a status display string showing current status or rating
            for this submission """
        if self.is_rated():
            return unicode(self.rating)
        return self.get_status_display()

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

    def get_STARS_rating(self, recalculate=False):
        """
            Return the STARS rating (potentially provisional) for this
            submission

            @todo: this is inefficient - need to store or at least cache
            the STARS score.
        """
        if (self.reporter_status or
            self.status == FINALIZED_SUBMISSION_STATUS or
            (not self.is_rated() and
             self.institution.access_level == BASIC_ACCESS)):
            return self.creditset.rating_set.get(name='Reporter')

        if self.is_rated() and not recalculate:
            return self.rating

        score = self.get_STARS_score(recalculate)
        return self.creditset.get_rating(score)

    def get_STARS_score(self, recalculate=False):
        """
            Return the total STARS score for this submission
            Relies on the scoring method defined by the CreditSet model.

             - define version-specific scoring methods below, and add
               to SCORING_METHOD_CHOICES in CreditSet model.
        """
        if self.status == 'r' and self.score and not recalculate:
            return self.score

        scoring_method = self.creditset.scoring_method
        if hasattr(self, scoring_method):
            score = getattr(self, scoring_method)
            if self.status == 'r':
                self.score = score()
                self.save()
            return score()
        else:
            logger.error(
                "No method (%s) defined to score submission %s" %
                (scoring_method, self.creditset.version))
            return 0

    def get_STARS_v1_0_score(self):
        """
            Averages of each category average
        """
        score = 0
        non_inno_cats = 0
        innovation_score = 0
        for cat in self.categorysubmission_set.all().select_related():
            if cat.category.is_innovation():
                innovation_score = cat.get_STARS_v1_0_score()
            elif cat.category.include_in_score:
                score += cat.get_STARS_v1_0_score()
                non_inno_cats += 1

        score = (score / non_inno_cats) if non_inno_cats > 0 else 0   # average

        score += innovation_score  # plus any innovation points

        return score if score <= 100 else 100

    def get_STARS_v2_0_score(self):
        """
            Percentage of total achieved out of total available
        """
        innovation_score = 0
        total_available = 0
        total_achieved = 0

        for cat in self.categorysubmission_set.all().select_related():
            if cat.category.is_innovation():
                innovation_score = cat.get_STARS_v2_0_score()
            elif cat.category.include_in_score:
                _score, _avail = cat.get_score_ratio()
                total_achieved += _score
                total_available += _avail

        score = total_achieved / total_available * 100

        score += innovation_score[0]  # plus any innovation points

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
        """ Gets only the points for credits that have not been labelled as
            Not Applicable """
        score = 0
        for cat in self.categorysubmission_set.all():
            score += cat.get_adjusted_available_points()
        return score

    def get_finished_credit_count(self):
        """ Get the number of credits that have been marked complete,
            not pursuing, or not applicable """
        count = 0
        for cat in self.categorysubmission_set.all():
            count += cat.get_finished_credit_count()
        return count

    def get_percent_complete(self):
        """ Return the percentage of credits completed in the entire
            set: 0 - 100 """
        total_credits = self.get_total_credits()
        if total_credits == 0:
            return 0
        return int(
            (self.get_finished_credit_count() / float(total_credits)) * 100)

    def get_progress_title(self):
        """ Returns a title for progress on the entire submission set """
        return "Complete" if (
            self.get_percent_complete() == 100) else "Reporting Status"

    def get_amount_due(self):
        """ Returns the amount of the total # of "later" payments tied to
            this submission """
        total = 0.0
        for p in self.payment_set.filter(type='later'):
            total += p.amount

        return total

    def init_credit_submissions(self):
        """
            Initializes all CreditUserSubmissions in a SubmissionSet
        """
        # Build the category list if necessary
        for category in self.creditset.category_set.all():
            try:
                categorysubmission = CategorySubmission.objects.get(
                    category=category, submissionset=self)
            except:
                categorysubmission = CategorySubmission(
                    category=category, submissionset=self)
                categorysubmission.save()

            # Create SubcategorySubmissions if necessary
            for subcategory in (
                    categorysubmission.category.subcategory_set.all()):
                try:
                    subcategorysubmission = SubcategorySubmission.objects.get(
                        subcategory=subcategory,
                        category_submission=categorysubmission)
                except SubcategorySubmission.DoesNotExist:
                    subcategorysubmission = SubcategorySubmission(
                        subcategory=subcategory,
                        category_submission=categorysubmission)
                    subcategorysubmission.save()

                # Create CreditUserSubmissions if necessary
                for credit in subcategory.credit_set.all():
                    try:
                        creditsubmission = CreditUserSubmission.objects.get(
                            credit=credit,
                            subcategory_submission=subcategorysubmission)
                    except CreditUserSubmission.DoesNotExist:
                        creditsubmission = CreditUserSubmission(
                            credit=credit,
                            subcategory_submission=subcategorysubmission)
                        creditsubmission.save()

    def get_credit_submissions(self):
        """Returns all the credit submissions for this SubmissionSet."""
        category_subs = CategorySubmission.objects.filter(
            submissionset=self)
        subcategory_subs = SubcategorySubmission.objects.filter(
            category_submission__in=category_subs)
        return CreditUserSubmission.objects.filter(
            subcategory_submission__in=subcategory_subs)

    def save(self, *args, **kwargs):
        # is this the first time save() has been called for self?
        run_init_credit_submissions = not self.pk
        super(SubmissionSet, self).save()  # assigns self.pk
        if run_init_credit_submissions:  # only run on initial save()
            # init_credit_submissions() will fail if self.pk is None,
            # so we wait until after super(...).save() assigns self.pk
            # a value:
            self.init_credit_submissions()

    def take_snapshot(self, user):
        """
            Creates a new SubmissionSet, based on this one, for the
            latest CreditSet.  Sends courtesy emails as well.
        """
        # Importing create_ss_mirror within take_snapshot() to avoid the
        # circular imports created when stars.apps.migrations.utils is
        # imported at the top level.
        from stars.apps.migrations.utils import create_ss_mirror

        # Participants keep their existing submission and save a duplicate
        new_ss = create_ss_mirror(self,
                                  new_cs=self.creditset,
                                  registering_user=user,
                                  keep_innovation=True,
                                  keep_status=True)

        new_ss.registering_user = user
        new_ss.date_registered = date.today()
        new_ss.date_submitted = date.today()
        new_ss.submitting_user = user
        new_ss.status = 'f'
        new_ss.is_visible = True
        new_ss.is_locked = False
        new_ss.save()

        et = EmailTemplate.objects.get(slug="snapshot_successful")
        to_mail = [user.email]
        if user.email != self.institution.contact_email:
            to_mail.append(self.institution.contact_email)
        et.send_email(to_mail, {'ss': self})

    def get_org_type(self):
        """Return the org type for the institution associated with this
        submissionset.

        For creditsets >= 2.0, pull the org type off the institution
        boundary credit.  For others, pull from the institution record.
        """
        if self.creditset.version > '2.':
            institutional_characteristics_category = Category.objects.get(
                abbreviation='IC')
            institutional_characteristics_credit_submissions = (
                self.get_credit_submissions().filter(
                    subcategory_submission__category_submission__category=
                    institutional_characteristics_category))
            boundary_credit_submission = (
                institutional_characteristics_credit_submissions.get(
                    credit__title='Institutional Boundary'))
            boundary_credit_submission_fields = (
                boundary_credit_submission.get_submission_fields())
            institution_type_submission_field = filter(
                lambda x: x.documentation_field.title == 'Institution type',
                boundary_credit_submission_fields)[0]
            return institution_type_submission_field.get_human_value()
        else:
            return self.institution.org_type


INSTITUTION_TYPE_CHOICES = (("associate", "Associate"),
                            ("baccalaureate", "Baccalaureate"),
                            ("master", "Master"),
                            ("doctorate", "Doctorate"),
                            ("special_focus", "Special Focus"),
                            ("tribal", "Tribal")
                            )

INSTITUTION_CONTROL_CHOICES = (("public", "Public"),
                               ("private_profit", "Private for-profit"),
                               ("private_nonprofit", "Private non-profit"))

FEATURES_CHOICES = ((True, 'Yes'),
                    (False, 'No'))


class Boundary(models.Model):
    """
        Defines the boundary for the submission set.
    """

    submissionset = models.OneToOneField(SubmissionSet)

    # Characteristics
    fte_students = models.IntegerField("Full-time Equivalent Enrollment", blank=True, null=True)
    undergrad_count = models.IntegerField("Number of Undergraduate Students", blank=True, null=True)
    graduate_count = models.IntegerField("Number of Graduate Students", blank=True, null=True)
    fte_employmees = models.IntegerField("Full-time Equivalent Employees", blank=True, null=True)
    institution_type = models.CharField(max_length=32, choices=INSTITUTION_TYPE_CHOICES, blank=True, null=True)
    institutional_control = models.CharField(max_length=32, choices=INSTITUTION_CONTROL_CHOICES, blank=True, null=True)
    endowment_size = models.BigIntegerField(blank=True, null=True)
    student_residential_percent = models.FloatField('Percentage of students that are Residential', blank=True, null=True)
    student_ftc_percent = models.FloatField('Percentage of students that are Full-time commuter', blank=True, null=True, help_text="Please indicate the percentage of full-time enrolled students that commute to campus.")
    student_ptc_percent = models.FloatField('Percentage of students that are Part-time commuter', blank=True, null=True, help_text='Please indicate the percentage of part-time enrolled students that commute to campus.')
    student_online_percent = models.FloatField('Percentage of students that are On-line only', blank=True, null=True)
    gsf_building_space = models.FloatField("Gross square feet of building space", blank=True, null=True, help_text="For guidance, consult <a href='http://nces.ed.gov/pubs2006/ficm/content.asp?ContentType=Section&chapter=3&section=2&subsection=1' target='_blank'>3.2.1 Gross Area (Gross Square Feet-GSF)</a> of the U.S. Department of Education's Postsecondary Education Facilities Inventory and Classification Manual.")
    gsf_lab_space = models.FloatField("Gross square feet of laboratory space", help_text='Scientific research labs and other high performance facilities eligible for <a href="http://www.labs21century.gov/index.htm" target="_blank">Labs21 Environmental Performance Criteria</a> (EPC).', blank=True, null=True)
    cultivated_grounds_acres = models.FloatField("Acres of cultivated grounds", help_text="Areas that are landscaped, planted, and maintained (including athletic fields). If less than 5 acres, data not necessary.", blank=True, null=True)
    undeveloped_land_acres = models.FloatField("Acres of undeveloped land", help_text="Areas without any buildings or development. If less than 5 acres, data not necessary", blank=True, null=True)
    climate_region = models.ForeignKey(ClimateZone, help_text="See the <a href='http://apps1.eere.energy.gov/buildings/publications/pdfs/building_america/ba_climateguide_7_1.pdf'>USDOE</a> site and <a href='http://www.ashrae.org/File%20Library/docLib/Public/20081111_cztables.pdf'>ASHRAE</a>  (international) for more information.", blank=True, null=True)

    # Features
    ag_school_present = models.NullBooleanField(
        "Agricultural school is present", choices=FEATURES_CHOICES, null=True)
    ag_school_included = models.NullBooleanField(
        "Agricultural school is included in submission",
        choices=FEATURES_CHOICES, null=True)
    ag_school_details = models.TextField("Reason for Exclusion", blank=True,
                                         null=True)
    med_school_present = models.NullBooleanField("Medical school is present",
                                                 choices=FEATURES_CHOICES,
                                                 null=True)
    med_school_included = models.NullBooleanField(
        "Medical school is included in submission", choices=FEATURES_CHOICES,
        null=True)
    med_school_details = models.TextField("Reason for Exclusion",
                                          blank=True, null=True)
    pharm_school_present = models.NullBooleanField(
        "Pharmacy school is present", choices=FEATURES_CHOICES, null=True)
    pharm_school_included = models.NullBooleanField(
        "Pharmacy school is included in submission", choices=FEATURES_CHOICES,
        null=True)
    pharm_school_details = models.TextField("Reason for Exclusion", blank=True,
                                            null=True)
    pub_health_school_present = models.NullBooleanField(
        "Public health school is present", choices=FEATURES_CHOICES, null=True)
    pub_health_school_included = models.NullBooleanField(
        "Public health school is included in submission",
        choices=FEATURES_CHOICES, null=True)
    pub_health_school_details = models.TextField("Reason for Exclusion",
                                                 blank=True, null=True)
    vet_school_present = models.NullBooleanField(
        "Veterinary school is present", choices=FEATURES_CHOICES, null=True)
    vet_school_included = models.NullBooleanField(
        "Veterinary school is included in submission",
        choices=FEATURES_CHOICES, null=True)
    vet_school_details = models.TextField("Reason for Exclusion",
                                          blank=True, null=True)
    sat_campus_present = models.NullBooleanField(
        "Satellite campuses are present", choices=FEATURES_CHOICES, null=True)
    sat_campus_included = models.NullBooleanField(
        "Satellite campuses are included in submission",
        choices=FEATURES_CHOICES, null=True)
    sat_campus_details = models.TextField("Reason for Exclusion",
                                          blank=True, null=True)
    hospital_present = models.NullBooleanField("Hospital is present",
                                               choices=FEATURES_CHOICES,
                                               null=True)
    hospital_included = models.NullBooleanField(
        "Hospital is included in submission", choices=FEATURES_CHOICES,
        null=True)
    hospital_details = models.TextField("Reason for Exclusion",
                                        blank=True, null=True)
    farm_present = models.NullBooleanField("Farm is present",
                                           help_text='Larger than 5 acres',
                                           choices=FEATURES_CHOICES, null=True)
    farm_included = models.NullBooleanField("Farm is included in submission",
                                            choices=FEATURES_CHOICES, null=True)
    farm_acres = models.FloatField("Number of acres", blank=True, null=True)
    farm_details = models.TextField("Reason for Exclusion", blank=True,
                                    null=True)
    agr_exp_present = models.NullBooleanField(
        "Agricultural experiment station is present",
        help_text='Larger than 5 acres', choices=FEATURES_CHOICES, null=True)
    agr_exp_included = models.NullBooleanField(
        "Agricultural experiment station is included in submission",
        choices=FEATURES_CHOICES, null=True)
    agr_exp_acres = models.IntegerField("Number of acres", blank=True,
                                        null=True)
    agr_exp_details = models.TextField("Reason for Exclusion", blank=True,
                                       null=True)

    # Narrative
    additional_details = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Boundaries"

    def __unicode__(self):
        return unicode(self.submissionset)

    def get_characteristic_fields_and_values(self):
        """
            This is a useful tool for displaying the boundary
        """
        f_set = []
        for field_name in self.__class__.get_characteristic_field_names():
            d = {'title': self._meta.get_field(field_name).verbose_name}
            if hasattr(self, "get_%s_display" % field_name):
                d['value'] = getattr(self, "get_%s_display" % field_name)
            else:
                d['value'] = getattr(self, field_name)

            f_set.append(d)

        return f_set

    @classmethod
    def get_characteristic_field_names(cls):
        return [
                    'fte_students',
                    'undergrad_count',
                    'graduate_count',
                    'fte_employmees',
                    'institution_type',
                    'institutional_control',
                    'endowment_size',
                    'student_residential_percent',
                    'student_ftc_percent',
                    'student_ptc_percent',
                    'student_online_percent',
                    'gsf_building_space',
                    'gsf_lab_space',
                    'cultivated_grounds_acres',
                    'undeveloped_land_acres',
                    'climate_region',
                ]

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
    score = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ("submissionset", "category")
        ordering = ("category__ordinal",)

    def __unicode__(self):
        return unicode(self.category)

    def get_crumb_label(self):
        return str(self)

    def get_crumb_url(self):
        return self.get_submit_url()

    def get_institution(self):
        return self.submissionset.institution

    def get_creditset(self):
        return self.submissionset.creditset

    def get_submit_url(self):
        return self.category.get_submit_url(submissionset=self.submissionset)

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

    def get_scorecard_url(self):
        cache_key = "category_%d_scorecard_url" % self.id
        url = cache.get(cache_key)
        if url:
            return url
        else:
            url = '%s%s' % (self.submissionset.get_scorecard_url(),
                            self.category.get_browse_url())
            cache.set(cache_key, url, 60*60*24) # cache for 24 hours
            return url

    def get_STARS_score(self):
        """
            Return the STARS score for this category
            - this is the fractional score for points earned in this category
            Relies on the scoring method defined for each credit set version:
             - define a version-specific method for each credit set below.
        """
        if self.submissionset.status == "r" and self.score:
            # cache the score in the model
            return self.score

        scoring_method = self.submissionset.creditset.scoring_method
        if hasattr(self, scoring_method):
            score = getattr(self, scoring_method)
            if self.submissionset.status == 'r':
                self.score = score()
                if type(self.score) == tuple:
                    self.score = self.score[0]
                self.save()
            return self.score
        else:
            logger.error(
                "No method (%s) defined to score category submission %s" %
                (scoring_method, self.submissionset.creditset.version))
            return 0

    def get_STARS_v1_0_score(self):
#        score = self.get_claimed_points()              # raw score - number of points earned in category
#        avail = self.get_adjusted_available_points()  # available / applicable points in category
        score, avail = self.get_score_ratio()
        #  score for innovation credits is just the raw score
        #  for all others, it is the proportion of points earned.
        if not self.category.is_innovation():
            score = ((100.0 * score) / avail) if avail>0 else 0   # percentage of points earned, 0 - 100
        return score

    def get_STARS_v2_0_score(self):
        """
            returns the available and achieved points
        """
        return self.get_score_ratio()

    def get_claimed_points(self):
        score = 0
        for sub in self.subcategorysubmission_set.all().select_related():
            score += sub.get_claimed_points()
        return score

    def get_available_points(self):
        score = 0
        for sub in self.subcategorysubmission_set.all().select_related():
            score += sub.get_available_points()
        return score

    def get_score_ratio(self):
        """
            Returns the claimed and adjusted available points
        """
        claimed = 0
        available = 0
        for sub in self.subcategorysubmission_set.all().select_related():
            claimed += sub.get_claimed_points()
            available += sub.get_adjusted_available_points()
        return claimed, available

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
    description = models.TextField(blank=True, null=True)
    points = models.FloatField(blank=True, null=True)
    # caching for the data displays
    percentage_score = models.FloatField(blank=True, null=True, default=0.0)
    adjusted_available_points = models.FloatField(blank=True, null=True,
                                                  default=0.0)

    class Meta:
        unique_together = ("category_submission", "subcategory")
        ordering = ("subcategory__ordinal",)

    def __unicode__(self):
        return unicode(self.subcategory)

    def get_crumb_label(self):
        return str(self)

    def get_crumb_url(self):
        return self.get_submit_url()

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

    def get_submissionset(self):
        return self.category_submission.submissionset

    def get_submit_url(self):
        return self.subcategory.get_submit_url(
            submissionset=self.category_submission.submissionset)

    def get_submit_edit_url(self):
        return self.subcategory.get_submit_edit_url(
            submissionset=self.category_submission.submissionset)

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
        rated = self.category_submission.submissionset.status == "r"
        # check the cache
        if rated and self.points and self.percentage_score:
            return self.points

        score = 0
        for credit in self.creditusersubmission_set.filter(submission_status='c'):
            score += credit.assessed_points

        if self.category_submission.submissionset.status == "r":
            # cache it on the model
            self.points = score
            available = self.get_available_points()
            if available > 0:
                self.percentage_score = score / available
            else:
                self.percentage_score = 0
            self.save()
        return score

    def get_available_points(self):
        points = 0
        for credit in self.subcategory.credit_set.all():
            points += credit.point_value
        return points

    def get_adjusted_available_points(self):
        """ Gets only the points for credits that have not been labelled as Not Applicable """

        rated = self.category_submission.submissionset.status == "r"
        # check the cache
        if rated and self.adjusted_available_points:
            return self.adjusted_available_points

        points = 0
        for credit_submission in self.creditusersubmission_set.all():
            points += credit_submission.get_adjusted_available_points()

        if rated:
            # cache the result
            self.adjusted_available_points = points
            self.save()
        return points

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

    def get_manage_url(self):
        return "/tool/{slug}/manage/responsible-party/{id}/".format(
              slug=self.institution.slug, id=self.id)

    def get_creditusersubmissions(self, order_by=None):
        """
            Returns a queryset of (visible) CreditUserSubmissions related to
            this responsible party.

            order_by arg is a tuple passed to queryset.order_by.
        """
        order_by = order_by or ('credit__subcategory__category__creditset',
                                'credit__subcategory')
        qs = self.creditusersubmission_set
        qs = qs.order_by(*order_by)
        qs = qs.exclude(subcategory_submission__category_submission__submissionset__is_visible=False)
        return qs


class CreditSubmission(models.Model):
    """
        A complete submission data set for a credit
        This is really an abstract base class for two types of submissions:

         - a User Submission (normal submission for an institutions
           STARS submission set)

         - a Test Submission (a test case used to validate formulae in
           the Credit Editor)
    """
    credit = models.ForeignKey(Credit)
    available_point_cache = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ("credit__type", "credit__ordinal",)

    def __unicode__(self):
        return self.credit.title

    def model_name():
        return u"Credit Submission"
    model_name = staticmethod(model_name)

    def __init__(self, *args, **kwargs):
        super(CreditSubmission, self).__init__(*args, **kwargs)
        self.submission_fields = None  # lazy init

    def get_crumb_label(self):
        return str(self)

    def get_institution(self):
        return self.subcategory_submission.get_institution()

    def get_submission_fields(self):
        """
            Returns the list of documentation field submission objects for
            this credit submission

            You can't simply ask
            self.documentationfieldsubmission_set.all() because each
            field may have a different type.

            If this CreditSubmission persists in DB, this method also
            saves empty submission field records for any that are
            missing.

            @return the complete list of DocumentationFieldSubmission
            sub-class objects related to this CreditSubmission
        """
        if not self.submission_fields:  # cache.
            self.submission_fields = self._submission_fields_for_documentation_fields(
                self.credit.documentationfield_set.all())

        return self.submission_fields

    def get_public_submission_fields(self):

        return self._submission_fields_for_documentation_fields(
            self.credit.documentationfield_set.filter(is_published=True))

    def _submission_fields_for_documentation_fields(self,
                                                    documentation_field_list):

        # Create the list of submission fields.
        errors = False

        submission_field_list = []
        for field in documentation_field_list:
            SubmissionFieldModelClass = (
                DocumentationFieldSubmission.get_field_class(field))
            if SubmissionFieldModelClass:
                try:
                    submission_field = SubmissionFieldModelClass.objects.get(
                        documentation_field=field, credit_submission=self)
                    # ORM / Model Inheritance issue:
                    #
                    #   DocumentationFieldSubmission has a foreign key to
                    #   CreditSubmission, but object may have reference to
                    #   a sub-class!
                    #
                    #   Hack: (Joseph)  update the reference in the field
                    #   we just loaded.
                    submission_field.credit_submission = self

                except SubmissionFieldModelClass.DoesNotExist:
                    submission_field = SubmissionFieldModelClass(
                        documentation_field=field, credit_submission=self)
                    submission_field.save()
                submission_field_list.append(submission_field)
            else:
                # use a dummy submission_field for tabular
                class TabularSubmissionField():
                    def __init__(self, credit_submission, documentation_field):
                        self.credit_submission = credit_submission
                        self.documentation_field = documentation_field
                        self.documentation_field_id = documentation_field.id

                    def get_value(self):
                        #dummy
                        return None

                    def get_human_value(self):
                        return ""

                submission_field_list.append(TabularSubmissionField(
                      credit_submission=self,
                      documentation_field=field))

        self.submission_fields = submission_field_list
        return self.submission_fields

    def get_submission_field_values(self):
        """ Returns the list of documentation field values for this
            submission
        """
        return [field.get_value() for field in self.get_submission_fields()]

    def get_submission_field_key(self):
        """ Returns a dictionary with identifier:value for each submission
            field
        """
        fields = self.get_submission_fields()
        key = {}
        for field in fields:
            key[field.documentation_field.identifier] = field.get_value()
        return key

    def print_submission_fields(self):
        print >> sys.stderr, "Fields for CreditSubmission: %s" % self
        fields = self.get_submission_fields()
        for field in fields:
            print >> sys.stderr, field

    # @todo: rename or remove this - potential confusion b/c name conflict
    #        with CreditUserSubmission!!
    #        I don't think this one is actually called anywhere.
    def is_complete(self):
        """ Return True if the Credit Submission is complete."""
        if not self.persists():
            # New submissions are incomplete - don't try to access fields yet!
            return False
        for field in self.get_submission_fields():
            if field.documentation_field.is_required() and not field.value:
                return False
        return True

    def is_test(self):
        """Returns True if this is a test submission."""
        return hasattr(self, 'credittestsubmission')

    def persists(self):
        """Does this CreditSubmission persist in the DB?"""
        return (not self.pk == None)

    def get_available_points(self, use_cache=False):
        if use_cache and self.available_point_cache != None:
            return self.available_point_cache
        # in most cases there's a fixed point value
        if self.credit.point_minimum == None:
            self.available_point_cache = self.credit.point_value
            return self.credit.point_value
        # but if there's not then we need to execute the formula
        else:
            (ran, message, exception, available_points) = self.credit.execute_point_value_formula(self)
            self.available_point_cache = available_points
            return available_points

    @staticmethod
    def round_points(points, log_error=True):
        """
            Convert points to numeric and round to the correct # decimals
            Returns (points, error) where

                - points = rounded numeric point value (or 0 if an
                  error occurred)

                - error = error message or None if conversion was successful
        """
        try: # Ensure that the result of the formula was a valid points value!
            points = float(points)
            return (round(points, 2), None)
        except Exception, e:
            if log_error:
                logger.error(
                    "Error converting formula result (%s) to numeric type: %s"
                    % (points,e), exc_info=True)
            return (0,
                    "Non-numeric result calculated for points: %s" % points)

    def validate_points(self, points, log_error=True):
        """
             Helper: Validate the points calculated for this submission
             Returns (points, messages), where points are the validated points

             - message is a list of error messages associated with any
               validation errors, which is empty if the the points
               validated.
        """
        messages = []

        # is it numeric?
        points, numeric_error = self.round_points(points, log_error)
        if numeric_error:
            messages.append(numeric_error)

        if points < 0 or points > self.credit.point_value:  # is it in range?
            range_error = ("Points (%s) are out of range (0 - %s)." %
                           (points, self.credit.point_value))
            if log_error:
                logger.error(range_error)
            messages.append(range_error)
            points = 0

        return points, messages

#    def __str__(self):  #  For DEBUG - comment out __unicode__ method above
#        if self.persists(): persists="persists"
#        else: persists="not saved"
#        return "<CreditSubmission %s credit_id=%s  %s>"%(
#                self.id, self.credit.id, persists)


CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED = [
    ('c', 'Complete'),
    ('p', 'In Progress'),
    ('np', 'Not Pursuing'),
]

# The 'ns' option isn't accessible in forms and 'na' only sometimes, so
# we 3 different lists.
CREDIT_SUBMISSION_STATUS_CHOICES_W_NA = list(
    CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED)
CREDIT_SUBMISSION_STATUS_CHOICES_W_NA.append(('na', 'Not Applicable'))
CREDIT_SUBMISSION_STATUS_CHOICES = list(CREDIT_SUBMISSION_STATUS_CHOICES_W_NA)
CREDIT_SUBMISSION_STATUS_CHOICES.append(('ns', 'Not Started'))

# used by template tag to create iconic representation of status:
CREDIT_SUBMISSION_STATUS_ICONS = {
    'c'  : ('icon-ok', 'c'),
    'p'  : ('icon-pencil', '...'),
    'np' : ('icon-remove', '-'),
    'na' : ('icon-tag', '-'),
}


class CreditUserSubmission(CreditSubmission, FlaggableModel):
    """
        An individual submitted credit for an institutions STARS submission
        set
    """
    subcategory_submission = models.ForeignKey(SubcategorySubmission)
    assessed_points = models.FloatField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    submission_status = models.CharField(
        max_length=8,
        choices=CREDIT_SUBMISSION_STATUS_CHOICES,
        default='ns')
    applicability_reason = models.ForeignKey(ApplicabilityReason,
                                             blank=True,
                                             null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    internal_notes = models.TextField(
        help_text=('This field is useful if you want to store notes for '
                   'other people in your organization regarding this credit. '
                   'They will not be published.'),
        blank=True,
        null=True)
    submission_notes = models.TextField(
        help_text=('Use this space to add any additional information '
                   'you may have about this credit. This will be published '
                   'along with your submission.'),
        blank=True,
        null=True)
    responsible_party_confirm = models.BooleanField()
    responsible_party = models.ForeignKey(ResponsibleParty,
                                          blank=True,
                                          null=True)

    class Meta:
        # @todo: the unique clause needs to be added at the DB level now :-(
        # unique_together = ("subcategory_submission", "credit")
        pass

    def get_submit_url(self):
        category_submission = self.subcategory_submission.category_submission
        submissionset = category_submission.submissionset
        url = urlresolvers.reverse(
            'creditsubmission-submit',
            kwargs={
                'institution_slug': submissionset.institution.slug,
                'submissionset': submissionset.id,
                'category_abbreviation': category_submission.category.abbreviation,
                'subcategory_slug': self.subcategory_submission.subcategory.slug,
                'credit_identifier': self.credit.identifier})
        return url

    def get_scorecard_url(self):
        cache_key = "cus_%d_scorecard_url" % self.id
        url = cache.get(cache_key)
        if url:
            return url
        else:
            url = self.credit.get_scorecard_url(
                self.subcategory_submission.category_submission.submissionset)
            cache.set(cache_key, url, 60*60*24) # cache for 24 hours
            return url

    def get_parent(self):
        """ Used for building crumbs """
        return self.subcategory_submission

    def get_creditset(self):
        return self.subcategory_submission.get_creditset()

    def get_submissionset(self):
        return self.subcategory_submission.get_submissionset()

    def is_finished(self):
        """ Indicate if this credit has been marked anything other than
            pending or not started
        """
        return (self.submission_status != 'p' and
                self.submission_status != 'ns' and
                self.submission_status != None)

    def save(self, *args, **kwargs):
        """ Override model.Model save() method to update credit status"""
        self.last_updated = datetime.now()
        self.assessed_points = float( self._calculate_points() )

        super(CreditUserSubmission, self).save(*args, **kwargs)

    def is_complete(self):
        return self.submission_status == 'c'

    def is_na(self):
        return self.submission_status == 'na'

    def is_pursued(self):
        """ Returns False if this credit is marked 'na' or 'np'  """
        return (self.submission_status != 'na' and
                self.submission_status != 'np')

    def mark_as_in_progress(self):
        self.submission_status = 'p'

    # def __str__(self):  # For DEBUG - comment out __unicode__ method above
    #     return ("<CreditUserSubmission:  %s>" %
    #             super(CreditUserSubmission,self).__str__())

    def get_adjusted_available_points(self):
        """ Gets only the points for credits that have not been labelled as
            Not Applicable
        """
        if self.submission_status == "na":
            return 0
        return self.get_available_points()

    def _calculate_points(self):
        """ Helper: returns the number of points calculated for this
        submission"""
        # Somewhat complex logic is required here so that i something goes
        # wrong, we log a detailed message, but only show the user meaningful
        # messages.
        if not self.is_complete(): # no points for incomplete submission
            return 0
        assessed_points = 0  # default is zero - now re-calculate points...
        validation_error = False

        (ran, message, exception, points, d) = self.credit.execute_formula(self, debug=True)

        if ran:  #perform validation on points...
            (points, messages) = self.validate_points(points)
            validation_error = len(messages) > 0

        if not ran or validation_error:
            logger.error("There was an error processing this credit. "
                         "AASHE has noted the error and will work to "
                         "resolve the issue.")
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

        (ran, msg, exception, points, debugging) = self.credit.execute_formula(self, debug=True)
        if ran:
            try:
                self.expected_value = float(self.expected_value)   # are we expecting a numeric result?
                (self.computed_value, messages) = self.validate_points(points)
                self.result = (abs(self.computed_value - self.expected_value) < 0.00001)  # Floating point equality to 5rd decimal place
            except (TypeError, ValueError):  # we're not expecting result to be numeric...
                self.computed_value = points
                self.result = self.computed_value == self.expected_value
        else:
            # Since this is test, substitute user-friendly
            # message for real error message.
            if isinstance(exception, AssertionError):
                messages.append('Assertion Failed: %s' % exception)
            elif exception:
                messages.append('Formula Error: %s' % exception)
            else:
                messages.append(msg)

        return (len(messages) > 0, messages, debugging)

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
        return ', '.join([field.__unicode__() for field in self.get_submission_fields()])

    def __unicode__(self):
        return "f( %s ) = %s" % (self.parameter_list(), self.expected_value)

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

class DataCorrectionRequest(models.Model):
    """
        A request by an institution to make a change to their submission
    """
    date = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    reporting_field = generic.GenericForeignKey('content_type', 'object_id')
    new_value = models.TextField(
        help_text="Note: if this is a numeric field, be sure to use the institution's preference for metric/imperial. You can find this in their settings.")
    explanation = models.TextField()
    user = models.ForeignKey(User, blank=True, null=True)
    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return self.reporting_field.documentation_field.title

    def get_absolute_url(self):
        """
            used to link back to the report from the admin
        """
        cus = CreditUserSubmission.objects.get(pk=self.reporting_field.credit_submission.id)
#         ss = cus.subcategory_submission.category_submission.submissionset
        return cus.get_scorecard_url()

    def get_submissionset(self):
        " used to display the submission set in the admin's list_display"
        cus = CreditUserSubmission.objects.get(pk=self.reporting_field.credit_submission.id)
        return cus.subcategory_submission.category_submission.submissionset

    def get_required_status(self):
        """
            Used by the admin to indicate if a field is conditionally required
            based on another field
        """
        return self.reporting_field.documentation_field.get_required_display()

    def get_credit(self):
        " Return the credit for the admin list"
        return self.reporting_field.documentation_field.credit

    def save(self):
        """
            Check the approved property to see if this was approved
            If so, confirm that the correction has been applied
        """
        if self.approved:
            try:
                c = self.applied_correction
            except ReportingFieldDataCorrection.DoesNotExist:
                self.approve()

        return super(DataCorrectionRequest, self).save()

    # def will_change_score(self):
    #     """
    #         A quick function to determine if an institution's score will change
    #         as a result of this correction
    #     """
    #     cus = CreditUserSubmission.objects.get(pk=self.reporting_field.credit_submission.id)
    #
    #
    # def new_score(self):
    #     """
    #         Calculates the new score before
    #     """


    def approve(self):
        """
            Approving a correction request creates a ReportingFieldDataCorrection
        """
        prev_value = self.reporting_field.value
        if prev_value == None:
            prev_value = "--"
        rfdc = ReportingFieldDataCorrection(
                                            previous_value=prev_value,
                                            change_date = datetime.today(),
                                            reporting_field = self.reporting_field,
                                            explanation = self.explanation,
                                            request = self,
                                            )

        if self.reporting_field.documentation_field.type == "choice":
            self.reporting_field.value = Choice.objects.get(pk=int(self.new_value))
        elif self.reporting_field.documentation_field.type == "boolean":
            if self.new_value == "Yes":
                self.reporting_field.value = True
            elif self.new_value == "No":
                self.reporting_field.value = False
            else:
                self.reporting_field.value = None

            if rfdc.previous_value == True:
                rfdc.previous_value = "Yes"
            elif rfdc.previous_value == False:
                rfdc.previous_value = "No"
            else:
                rfdc.previous_value = "Unknown"
        elif self.reporting_field.documentation_field.type == "numeric":
            # unit conversion handled by the save() method on the model
            if self.reporting_field.use_metric():
                if self.reporting_field.value != None:
                    rfdc.previous_value = "%d %s" % (
                        self.reporting_field.metric_value,
                        self.reporting_field.documentation_field.metric_units)
                else:
                    rfdc.previous_value = "---"
                self.reporting_field.metric_value = float(self.new_value)
            else:
                if self.reporting_field.value != None:
                    rfdc.previous_value = "%d %s" % (
                        self.reporting_field.value,
                        self.reporting_field.documentation_field.us_units)
                else:
                    rfdc.previous_value = "---"
                self.reporting_field.value = float(self.new_value)

        else:
            self.reporting_field.value = self.new_value
        self.reporting_field.save()
        rfdc.save()
        self.approved = True

        # Apply change to overall score.
        cus = CreditUserSubmission.objects.get(pk=self.reporting_field.credit_submission.id)
        ss = cus.subcategory_submission.category_submission.submissionset
        score_changed = False
        rating_changed = False
        old_rating = ss.rating
        old_score = ss.score

        if cus.assessed_points != cus._calculate_points():
            cus.assessed_points = cus._calculate_points()
            cus.save()

            score_changed = True

            cus.subcategory_submission.points = None
            cus.subcategory_submission.points = cus.subcategory_submission.get_claimed_points()
            cus.subcategory_submission.save()

            cus.subcategory_submission.category_submission.score = None
            cus.subcategory_submission.category_submission.score = cus.subcategory_submission.category_submission.get_STARS_score()
            cus.subcategory_submission.category_submission.save()

            ss.score = None
            ss.score = ss.get_STARS_score()
            ss.save()

            new_rating = ss.get_STARS_rating(recalculate=True)
            if ss.rating != new_rating:
                ss.rating = new_rating
                ss.institution.current_rating = new_rating
                ss.institution.save()
                rating_changed = True
                ss.save()

        ss.pdf_report = None
        ss.save()

        # notify institution of approval
        et = EmailTemplate.objects.get(slug='approved_data_correction')
        mail_to = [ss.institution.contact_email,]
        if ss.institution.contact_email != self.user.email:
            mail_to.append(self.user.email)
        email_context = {
                            "submissionset": ss,
                            "credit_submission": cus,
                            "score_changed": score_changed,
                            "rating_changed": rating_changed,
                            "old_rating": old_rating,
                            "old_score": old_score,

                        }
        et.send_email(mail_to, email_context)

class ReportingFieldDataCorrection(models.Model):
    """
        Represents a change to a particular field in Credit Submission after
        an institution has received a rating.
    """
    request = models.OneToOneField(DataCorrectionRequest, related_name='applied_correction', blank=True, null=True)
    previous_value = models.TextField()
    change_date = models.DateField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    reporting_field = generic.GenericForeignKey('content_type', 'object_id')
    explanation = models.TextField(blank=True, null=True)


class DocumentationFieldSubmission(models.Model, FlaggableModel):
    """
        The submitted value for a documentation field (abstract).
    """
    documentation_field = models.ForeignKey(DocumentationField,
                                            related_name="%(class)s_set")
    credit_submission = models.ForeignKey(CreditSubmission)
    corrections = generic.GenericRelation(ReportingFieldDataCorrection,
                                          content_type_field='content_type',
                                          object_id_field='object_id')

    class Meta:
        abstract = True
        unique_together = ("documentation_field", "credit_submission")

    def __unicode__(self):
        """ return the title of this submission field """
        return self.documentation_field.__unicode__()

    def get_parent(self):
        """ Used for building crumbs """
        return self.credit_submission

    def get_institution(self):
        parent = CreditUserSubmission.objects.get(
            pk=self.credit_submission.id)
        return parent.get_institution()

    def get_creditset(self):
        return self.credit_submission.creditusersubmission.get_creditset()

    def get_submissionset(self):
        """Returns the SubmissionSet related to this
        DocumentationFieldSubmission.
        """
        return self.credit_submission.creditusersubmission.get_submissionset()

    def persists(self):
        """Does this Submission object persist in the DB?"""
        return (not self.pk == None)

    def get_field_class(field):
        """
           Returns the related DocumentationFieldSubmission model class for a
           particular documentation field
        """
        if field.type == 'text':
            return TextSubmission
        if field.type == 'long_text':
            return LongTextSubmission
        if field.type == 'numeric':
            return NumericSubmission
        if field.type == 'choice':
            return (ChoiceWithOtherSubmission
                    if field.has_other_choice()
                    else ChoiceSubmission)
        if field.type == 'multichoice':
            return (MultiChoiceWithOtherSubmission
                    if field.has_other_choice()
                    else MultiChoiceSubmission)
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

    def get_human_value(self):
        """
            Returns a human readable version of the value
        """
        if self.documentation_field.type == 'tabluar':
            return ""
        if self.documentation_field.type == 'upload':
            if self.value:
                return "http://stars.aashe.org%s" % self.value.url
            else:
                return ""
        else:
            # long text has to be truncated for excel
            if not self.value:
                return ""
            else:
                if self.documentation_field.type == 'long_text':
                    str_val = self.value.replace("\r\n", "\n")
                    if len(str_val) > 32000:
                        str_val = "%s ... [TRUNCATED]" % str_val[:32000]
                    return str_val

                elif self.documentation_field.type == 'numeric':

                    str_val = "%.2f" % self.value
                    if str_val[-3:] == '.00':
                        str_val = str_val[:-3]

                    units = self.documentation_field.units

                    if units:
                        return "%s %s" % (str_val, units)

                    return str_val

                elif self.documentation_field.type == "choice":
                    return self.value.choice

                else:
                    return self.value

    def save(self, *args, **kwargs):
        """ Override models.Model save() method to forstall save if
            CreditSubmission doesn't persist """
        # Only save submission fields if the overall submission has been saved.
        if self.credit_submission.persists():
            super(DocumentationFieldSubmission, self).save()

    def get_value(self):
        """ Use this accessor to get this submission's value - rather than
            accessing .value directly """
        return self.value

    def is_empty(self):
        if self.value == None or self.value == "":
            return True
        # if it's nothing but whitespace
        if re.match("^\s+$", self.value) != None:
            return True
        return False

    def get_correction_url(self):
        return "%s%d/" % (self.credit_submission.get_scorecard_url(),
                          self.documentation_field.id)


class AbstractChoiceSubmission(DocumentationFieldSubmission):
    class Meta:
        abstract = True

    def __unicode__(self):
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
    """
        A proxy model (does not create a new table) for a Choice
        Submission with an 'other' choice
    """
    class Meta:
        proxy = True

    def decompress(self, value):
        """
            Given a single value (the pk for a Choice object),
            return a list of the form: [choiceId, otherValue], where

             - choiceId is the id of the selection choice and
               otherValue is the the text value of the choice, if it
               is a non-bonafide (other) choice.

            This is really the decompress logic for a
            ChoiceWithOtherSelectWidget (MutliWidget), but needs to do
            "model"-type stuff, so it is passed to the widget via the
            form.
        """
        if not value:
            return [None, None]
        # The choice must be in the DB - this algorithm is not
        # foolproof - could use a little more thought.
        try:
            choice = Choice.objects.get(id=value)
        except:
            logger.error("Attempt to decompress non-existing Choice (id=%s)" %
                         value, exc_info=True)
            return [None, None]
        if choice.is_bonafide:  # A bonafide choice is one of the actual choices
            return [value, None]
        else:                   # whereas non-bonafide choices
                                #represent an 'other' choice.

            # value is not one of the bonafide choices - try to find
            # it in the DB.  The selection is the last choice, and the
            # Choice text is the 'other' field.
            return [self.get_last_choice().pk, choice.choice ]

    def compress(self, choice, other_value):
        """
            Given a decompressed choice / other value pair into a
            single Choice value

            Return a single Choice representing the selection, or
            None.

            Assumes choice is a Choice and other_value has been
            properly sanatized!

            See decompress() above, except compress is peformed during
            clean() in ModelChoiceWithOtherField
        """
        # Warn the user about potentially lost data
        last_choice = self.get_last_choice()
        if other_value and choice != last_choice:
            logger.warning(
                "'%s' will not be saved because '%s' was not selected." %
                (other_value, last_choice.choice))
        return super(ChoiceWithOtherSubmission, self).compress(choice,
                                                               other_value)


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

    def __unicode__(self):
        """ return a string representation of the submission' value """
        choices = self.get_value()
        if not choices:
            return "[ ]"
        return '[%s]' %','.join([self._get_str(choice) for choice in choices])


class MultiChoiceWithOtherSubmission(MultiChoiceSubmission,
                                     AbstractChoiceWithOther):
    """
        A proxy model (does not create a new table) for a MultiChoice
        Submission with an 'other' choice
    """
    class Meta:
        proxy = True

    def decompress(self, value):
        """
            Given a list of values (list of pk for Choice objects),
            return a list of the form: [[choiceId1, choiceId2],
            otherValue], where

             - choiceId's are the id's of the selected choices and
               otherValue is the the text value of the choice, if it
               is a non-bonafide (other) choice.

            This is really the decompress logic for a
            SelectMultipleWithOtherWidget (MutliWidget), but needs to
            do "model"-type stuff, so it is passed to the widget via
            the form.
        """
        if not value:
            return [[], None]
        # The choice must be in the DB - this algorithm is not
        # foolproof - could use a little more thought.
        choice_list=[]
        other = None
        for choice_id in value:
            try:
                choice = Choice.objects.get(id=choice_id)
            except:
                logger.error(
                    "Attempt to decompress non-existing Choice (id=%s)" %
                    choice_id, exc_info=True)
                return [[], None]
            if not choice.is_bonafide:  # An 'other' choice replace
                                        # the choice with the last
                                        # choice.
                if other:
                    logger.error(
                        "Found multiple 'other' choices "
                        "(%s and %s) associated with single "
                        "MultiChoiceWithOtherSubmission (id=%s)" %
                        (other, choice.choice, self.id))
                else:
                    choice_id = self.get_last_choice().pk
                    other = choice.choice
            choice_list.append(choice_id)

        return [choice_list, other]

    def compress(self, choices, other_value):
        """
            Given a decompressed choice list / other value pair into a
            single Choice list, return a list of Choices representing
            the selections, or None.

            Assumes choices is a list of Choices and other_value has
            been properly sanatized!

            See decompress() above, except compress is peformed during
            clean() in ModelMultipleChoiceWithOtherField
        """
        choice_list = []
        for choice in choices:
            choice_list.append(super(MultiChoiceWithOtherSubmission,
                                     self).compress(choice, other_value) )

        # Warn the user about potentially lost data
        last_choice = self.get_last_choice()
        if other_value and not last_choice in choices:
            logger.warning(
                "'%s' will not be saved because '%s' was not selected." %
                (other_value, last_choice.choice))

        return choice_list

class URLSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a URL Documentation Field
    """
    value = models.URLField(blank=True, null=True, verify_exists=False)

class DateSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Date Documentation Field
    """
    value = models.DateField(blank=True, null=True)


class NumericSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Numeric Documentation Field

        This DocumentationFieldSubmission has an extra field, `metric_value`

        Logic:
            The form and model use slightly different logic. The form needs to
            know if it should display the `value` or `metric_value` field. And
            the model needs to know if it should convert the data from one
            field to the other.

            This is handled with two methods:
                `requires_duplication` - uses the documentation field
                        - `DocumentationField` has a `units` and
                        - the `metric_units` and `us_units` are not the same
                            (MMBTU is metric, but used the US too)
                `use_metric` - uses institution preference

            Model:
                The model will save both fields when the other could be needed

                The times when population is needed
                    `value` to `metric_value`
                        - duplication required
                        - institutions prefers us units
                    `metric_value` to `value`
                        - duplication required
                        - institutions prefers metric units

                Otherwise, there is no need for the metric field to be
                populated

            Form:
                The form needs to display the correct field and validate.

                Picking the field:
                    `value`:
                        - if the institution doesn't prefer metric
                        - if the institution prefers metric, but duplication
                        isn't required
                    `metric_value`:
                        - if the institution prefers metric and duplication is
                        required

                Validating:
                    if displaying the `metric_field` populate the `value` field
                    prior to validating

            The logic description here is necessary, because these are coupled,
            since the model has to know which value field to use to populate
            the other. For example, if the institution's preference is for
            metric, but the form displays `value` because there are no units,
            then the
    """
    value = models.FloatField(blank=True, null=True)
    metric_value = models.FloatField(blank=True, null=True)

    def requires_duplication(self):
        """
            Determines if this instance needs to have both `value` and
            `metric_values` stored in the database
        """
        df = self.documentation_field
        return df.units and (df.us_units != df.metric_units)

    def use_metric(self):
        """
            Logic to determine if the `metric_value` field should be used. This
            is shared with the form, so it makes sense to add it to the model
        """
        if self.requires_duplication():
            institution = self.get_institution()
            return institution.prefers_metric_system
        return False

    def save(self, *args, **kwargs):
        """
            Override the save method to generate the metric value
        """
        # in most cases the following would have worked:
        # self.credit_submission.get_institution().prefers_metric_system
        # but when accessing the NumericSubmission directly, we need to connect
        # the correct CreditUserSubmission instead of CreditSubmission

        if self.requires_duplication():
            if self.use_metric():
                if self.metric_value is not None:
                    units = self.documentation_field.metric_units
                    self.value = units.convert(self.metric_value)
                else:
                    self.value = None
            else:
                if self.value:
                    units = self.documentation_field.us_units
                    self.metric_value = units.convert(self.value)
                else:
                    self.metric_value = None

        super(NumericSubmission, self).save(*args, **kwargs)


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
    value = models.FileField(
        upload_to=upload_path_callback,
        blank=True,
        null=True)

    def get_filename(self):
        """ Returns the name of the file w/out the full path. """
        return os.path.basename(self.value.name)

    def get_admin_url(self):
        url = urlresolvers.reverse(
            'admin:submissions_uploadsubmission_change',
            args=(self.id,))
        return url


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
    ('member_reg', 'member_reg'),
    ('nonmember_reg', 'nonmember_reg'),
    ('member_renew', 'member_renew'),
    ('nonmember_renew', 'nonmember_renew'),
    ('international', 'international')
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
    reason = models.CharField(max_length='16', choices=PAYMENT_REASON_CHOICES)
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

class SubmissionInquiry(models.Model):
    """
        An inquiry by a member of the public about any inaccurate data in a public report
    """

    submissionset = models.ForeignKey(SubmissionSet)
    date = models.DateTimeField(auto_now_add=True)
    anonymous = models.BooleanField()
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    affiliation = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=32, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    additional_comments = models.TextField(blank=True, null=True, help_text="Include any other comments about the Submission, including the Submission Boundary and Subcategory Descriptions.")

    class Meta:
        verbose_name_plural = "Submission Inquiries"

    def __unicode__(self):
        return self.submissionset.institution.name


class CreditSubmissionInquiry(models.Model):
    """
        An inquiry, tied to a SubmissionInquiry about a particular credit.
    """

    submission_inquiry = models.ForeignKey(SubmissionInquiry)
    credit = models.ForeignKey(Credit)
    explanation = models.TextField()

    class Meta:
        verbose_name_plural = "Credit Submission Inquiries"

    def __unicode__(self):
        return self.credit.title


class ExtensionRequest(models.Model):
    """
        Schools can request a 6 month extension for their submission
    """

    submissionset = models.ForeignKey(SubmissionSet)
    old_deadline = models.DateField()
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return str(self.date)


class SubcategoryOrgTypeAveragePoints(models.Model):
    """The average points for a Subcategory and Institution.org_type.
    """
    subcategory = models.ForeignKey(Subcategory)
    org_type = models.CharField(max_length=32)
    average_points = models.FloatField(default=0)

    class Meta:
        unique_together = ("subcategory", "org_type")

    def calculate(self):
        """Calculate the average.  Only count rated submissions.
        """
        subcategory_submissions = SubcategorySubmission.objects.filter(
            subcategory=self.subcategory,
            category_submission__submissionset__status='r')
        total_points = total_submissions = 0
        for subcategory_submission in subcategory_submissions:
            if (subcategory_submission.get_submissionset().get_org_type() ==
                self.org_type):

                total_points += subcategory_submission.get_claimed_points()
                total_submissions += 1
        if total_submissions:
            self.average_points = total_points / total_submissions
        else:
            self.average_points = 0
        self.save()
        logger.debug('For subcategory: {subcategory}, org_type: {org_type}: '
                     'average_points: {average_points}'.format(
                         subcategory=self.subcategory,
                         org_type=self.org_type,
                         average_points=self.average_points))


class SubcategoryQuartiles(models.Model):
    """Cached statistics for Subcategories.

    Caches the quartiles for submissions, grouped by subcategory and org_type.

    Values cached (first, second, third, fourth) are the highest numbers
    of each quartile.  The numbers represent the percentage of available
    points granted to a submission, not the number of points granted.
    """
    subcategory = models.ForeignKey(Subcategory)
    org_type = models.CharField(max_length=32)
    first = models.FloatField(default=0)
    second = models.FloatField(default=0)
    third = models.FloatField(default=0)
    fourth = models.FloatField(default=0)

    class Meta:
        unique_together = ("subcategory", "org_type")

    def calculate(self):
        """Calculate the quartiles.  Only count rated submissions.
        """
        subcategory_submissions = SubcategorySubmission.objects.filter(
            subcategory=self.subcategory,
            category_submission__submissionset__status='r')
        points_percent = []

        for subcategory_submission in subcategory_submissions:
            if (subcategory_submission.get_submissionset().get_org_type() ==
                self.org_type):

                adjusted_available_points = (
                    subcategory_submission.get_adjusted_available_points())

                if adjusted_available_points:

                    points_percent.append(
                        (subcategory_submission.get_claimed_points() /
                         adjusted_available_points) * 100)

        if sum(points_percent):
            array = numpy.array(points_percent)
            self.first, self.second, self.third, self.fourth = (
                numpy.percentile(array, numpy.arange(0, 100, 25)))
        else:
            self.first = self.second = self.third = self.fourth = 0
        self.save()
