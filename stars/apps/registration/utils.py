from stars.apps.institutions.models import *
from stars.apps.submissions.models import *

import re

def is_canadian_zipcode(zipcode):
    """
        Validates a Canadian zip code
    """
    pattern = "^[a-zA-Z]\d[a-zA-Z][ -]*\d[a-zA-Z]\d$"
    return bool(re.match(pattern, zipcode))
    
def is_usa_zipcode(zipcode):
    """
        Validates a USA zip code
    """
    pattern = "^\d\d\d\d\d$"
    return bool(re.match(pattern, zipcode))

def get_orphaned_submissionsets():
    """
        Finds SubmissionSets that don't have an Institution
    """
    return get_orphans(SubmissionSet, 'institution')
            
def get_orphaned_payments():
    """
        Find any payments that don't have a parent SubmissionSet
    """
    return get_orphans(Payment, 'submissionset')

def get_orphans(klass, parentClass):
    """
        Find all klass-types that are missing their parentClass
        @Todo: maybe we'll include this in helpers/utils eventually
    """
    orphans = []
    for k in klass.objects.all():
        try:
            p = k.__getattribute__(parentClass)
        except:
            orphans.append(k)
    return orphans