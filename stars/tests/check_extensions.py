from stars.apps.submissions.models import *

from datetime import datetime

for ss in SubmissionSet.objects.exclude(status='r').filter(submission_deadline__gte=datetime.now()):
    td = ss.submission_deadline - ss.date_registered
    # check if they have more than 365 days to submit. Did they get an extension?
    if td.days > 365:
        if ss.extensionrequest_set.count() > 0:
            if td.days > 700:
                print "********%s" % ss.institution
        else:
            print "[%s]%s - %s: %s" % (td.days, ss.date_registered, ss.submission_deadline, ss.institution)
            # print ss.institution