import datetime
import sys

from stars.apps.institutions.models import Institution
from stars.apps.migrations.utils import create_ss_mirror

def update_institution_properties():
    """
        Nightly cron to maintain institution properties:
            is_participant
            current_subscription
            current_rating
    """
    for i in Institution.objects.all():
        # if their subscription has expired
        if i.current_subscription and i.current_subscription.end_date < datetime.date.today():
            print >> sys.stdout, "Expired Subscription: %s" % i
            print >> sys.stdout, i.current_subscription.end_date
            i.current_subscription = None
            i.is_participant = False
        # if they don't have a subscription (this isn't likely, but still possible)
        if i.current_subscription == None:
            print >> sys.stdout, "Expired Participant: %s" % i
            i.is_participant = False
        # once their rating has expired
        if i.rating_expires and i.rating_expires < datetime.date.today():
            print >> sys.stdout, "Expired Rating: %s" % i
            i.rating_expires = None
            i.rating = None
        i.save()
        
def update_submissions():
    """
        Create new submissions when:
            - an institution's current submission is rated
    """
    for i in Institution.objects.all():
        old_ss = None
        if i.current_submission and i.current_submission.status == 'r':
            old_ss = i.current_submission
        elif i.current_submission == None:
            old_ss = i.get_latest_rated_submission()
        if old_ss:
            new_ss = create_ss_mirror(old_ss)
            new_ss.is_locked = False
            new_ss.is_visible = True
            new_ss.save()
            i.current_submission = new_ss
            i.save()
            