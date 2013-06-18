print "rated submissions that are the most recent but not listed as current"

from stars.apps.institutions.models import Institution

for i in Institution.objects.all():
    qs = i.submissionset_set.filter(status='r')
    if qs.count() > 0:
        ss = qs.order_by('-date_submitted')[0]
        if i.rated_submission == ss:
            print i

print "rated submissions that aren't visisble"

from stars.apps.submissions.models import SubmissionSet

for ss in SubmissionSet.objects.filter(status='r').filter(is_visible=False):
    print ss
