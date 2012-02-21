import datetime
import sys

from stars.apps.institutions.models import Institution
from stars.apps.migrations.utils import create_ss_mirror
from stars.apps.registration.views import init_submissionset
from stars.apps.helpers import watchdog

def update_institution_properties():
    """
        Nightly cron to maintain institution properties:
            is_participant
            current_subscription
            current_rating
    """
    for i in Institution.objects.all():
#        print >> sys.stdout, "Checking %s" % i.name
        # if their subscription has expired
        if i.current_subscription and i.current_subscription.end_date < datetime.date.today():
            print >> sys.stdout, "Subscription Expired on %s for %s" % (i.current_subscription.end_date, i)
            
            watchdog.log("Sub_cron", "Subscription Expired for %s" % i, watchdog.NOTICE)
            i.current_subscription = None
            i.is_participant = False
            # @todo: send email
            
            # check to see if there are any current subscriptions
            if i.current_subscription == None:
                for s in i.subscription_set.all():
                    if s.start_date < datetime.date.today() and s.end_date > datetime.date.today():
                        watchdog.log("Sub_cron", "New Subscription found for %s" % i, watchdog.NOTICE)
                        print >> sys.stdout, "Renewal Found."
                        i.current_subscription = s
                        i.is_participant = True
            
            # if there is still no subscription create an empty submission
            # to be the current submission
            if i.current_subscription == None:
                try:
                    u = i.current_submission.registering_user
                    i.current_submission = init_submissionset(i, u)
                except SubmissionSet.DoesNotExist:
                    print >> sys.stderr, "No Current Submission found for %s" % i
                    watchdog.log("Sub_cron", "No Current Submission for %s" % i, watchdog.ERROR)
            
            i.save()
            
update_institution_properties()