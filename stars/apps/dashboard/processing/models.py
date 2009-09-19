from django.db import models

from stars.apps.credits.models import *

class SubmissionSet(models.Model):
    creditset = models.ForeignKey(CreditSet)
    