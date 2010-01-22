from stars.apps.institutions.models import *
from stars.apps.submissions.models import *

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