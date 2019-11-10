from datetime import timedelta, date

from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import SubmissionSet


to_fix = []


for institution in Institution.objects.all():
    rated_submissions = institution.submissionset_set.filter(status='r')
    if rated_submissions.count() > 0:
        latest_rated_submission = rated_submissions.order_by(
            '-date_submitted')[0]
        if institution.rated_submission != latest_rated_submission:
            i.current_rating = ss.rating
            i.rated_submission = ss
            i.rating_expires = date.today() + timedelta(days=365*3)
            i.save()
