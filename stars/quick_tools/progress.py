#!/usr/bin/env python

"""
    Print institutions with 0% progress
"""

from stars.apps.institutions.models import *
from stars.apps.submissions.models import SubmissionSet

print "Institution,Contact,Phone,Email,Deadline"

for ss in SubmissionSet.objects.order_by("institution__name"):
    if ss.get_percent_complete() == 0:
#        print "%s (%d)" % (ss.institution, ss.get_percent_complete())
        print "\"%s\", %s %s, %s, %s" % (ss.institution,
                                         ss.institution.contact_first_name,
                                         ss.institution.contact_last_name,
                                         ss.institution.contact_email)
