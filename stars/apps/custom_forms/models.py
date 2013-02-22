from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField

from stars.apps.credits.models import Subcategory

INST_CHOICES = (
    ('2-year', "2-year Associate's College"),
    ('baccalaureate', 'Baccalaureate College'),
    ('masters', "Master's Institution"),
    ('research', "Research University"),
    ('non-profit', "Non-profit Organization"),
    ('gov', 'Government Agency'),
    ('for-profit', "For-profit Business"),
    ('other', 'Other'),
)

class TAApplication(models.Model):
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    title = models.CharField(max_length=64)
    department = models.CharField(max_length=64)
    institution = models.CharField("Institution/Organization Affiliation", max_length=128)
    phone_number = PhoneNumberField()
    email = models.EmailField()
    address = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=5)
    instituion_type = models.CharField("Institution/Organization Type", max_length=32, choices=INST_CHOICES)
    subcategories = models.ManyToManyField(Subcategory)
    skills_and_experience = models.TextField()
    related_associations = models.TextField()
    resume = models.FileField(upload_to='ta_apps')
    credit_weakness = models.TextField(null=True, blank=True)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class DataDisplayAccessRequest(models.Model):
    " a request for temporary access to the Data Displays "
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    email = models.EmailField()
    affiliation = models.CharField("Institution or Affiliation", max_length=128)
    reason_for_request = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)


class SteeringCommitteeNomination(models.Model):
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    email = models.EmailField()
    affiliation = models.CharField("Institution or Affiliation", max_length=128)
    phone_number = PhoneNumberField()
    why = models.TextField("Why would you be excited to serve on the STARS Steering Committee?")
    skills = models.TextField("What specific skills or background would you bring to the STARS Steering Committee that would help advance STARS?")
    successful = models.TextField("How can you help STARS become a successful rating system?")
    strengths = models.TextField("What do you consider to be the strengths and weaknesses of STARS?")
    perspectives = models.TextField("What perspectives or representation of stakeholder groups would you bring to the STARS Steering Committee?")
    resume = models.FileField(upload_to='sc_apps')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

class EligibilityQuery(models.Model):
    name = models.CharField(max_length=64)
    title = models.CharField(max_length=128)
    email = models.EmailField()
    institution = models.CharField(max_length=128)
    requesting_institution = models.CharField(max_length=128, blank=True,
                                              null=True)
    other_affiliates = models.BooleanField()
    included_in_boundary = models.BooleanField()
    separate_administration = models.BooleanField()
    rationale = models.TextField()
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        if self.requesting_institution:
            return self.requesting_institution
        else:
            return self.institution
