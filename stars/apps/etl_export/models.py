from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField

from stars.apps.institutions.models import Institution
from stars.apps.credits.models import Rating
from stars.apps.submissions.models import SUBMISSION_STATUS_CHOICES

class ETL(models.Model):
    """
        This model houses all the required fields for the Salesforce Extract Transform and Load operation.
    """
    aashe_id = models.IntegerField()
    change_date = models.DateTimeField(auto_now=True)
    participant_status = models.CharField(max_length=32, choices=SUBMISSION_STATUS_CHOICES, blank=True, null=True)
    current_rating = models.CharField(max_length=16, null=True, blank=True)
    rating_valid_until = models.DateField(blank=True, null=True)
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
    
    def __str__(self):
        return "%d" % self.aashe_id
        
    def __eq__(self, obj):
        """
            Compares two ETL objects for equality. Compare everything except fo the change date and id
            Returns True if equal and False if not
        """
        
        exclude = ['change_date','id']
        for field in self._meta.get_all_field_names():
            if field not in exclude:
                if getattr(self, field) != getattr(obj, field):
                    return False
        return True
        
    def __ne__(self, obj):
        """
            Compares to ETL objects for inequality
        """
        return not (self == obj)
    