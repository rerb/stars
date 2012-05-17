import datetime
import sys

from stars.apps.institutions.models import Institution
from stars.apps.migrations.utils import create_ss_mirror
from stars.apps.registration.views import init_submissionset
from stars.apps.helpers import watchdog

def eval_participant_status(i):
    """
        Does the evaluation of participant status, instead of using
        the is_participant field
        
        returns (is_participant, current_subscription)
    """
    
    # see if there is a current subscription
    for sub in i.subscription_set.order_by('start_date'):
        if sub.start_date <= datetime.date.today() and sub.end_date >= datetime.date.today():
            return (True, sub)
    
    return (False, None)
    
def eval_rated_submission(i):
    """
        Get the latest rated submission set for an institution
        
        @todo test chronological order
    """
    
    try:
        return i.submissionset_set.filter(status='r').order_by('-date_submitted')[0]
    except:
        return None

def update_institution_properties():
    """
        Nightly cron to maintain institution properties:
            is_participant
            current_subscription
            current_rating, rated_submission
            
            evaluate is_participant
            evaluate current_subscription
            evaluate current_rating

            compare with existing values
            
            if changed:
                check for subscription expiration
                    send email
                    create empty submission
                check for rating expiration
                    send email
    """
    
    for i in Institution.objects.all():
        
        is_participant, current_subscription = eval_participant_status(i)
        rated_submission = eval_rated_submission(i)
        
        # Participation Status
        
        if i.is_participant != is_participant:
            
            # if participation status has changed
            
            if not i.is_participant:
                # renewal: wasn't an now is
                i.is_participant = True
                if i.current_subscription:
                    print >> sys.stdout, "Inconsistent status w/ subscription for %s" % i
                i.current_subscription = current_subscription
                print >> sys.stdout, "Found subscription for %s" % i
            else:
                # expiration: was an now isn't
                i.is_participant = False
                i.current_subscription = None
                print >> sys.stdout, "%s subscription expired" % i
                #@todo email institution
            i.save()
            
        else:
            
            # check if there's a rollover subscription
            if i.current_subscription != current_subscription:
                i.current_subscription = current_subscription
                print >> sys.stdout, "%s had a rollover subscription" % i
                i.save()
                
        # Rating
        
        if i.rated_submission != rated_submission:
            
            if rated_submission == None:
                
                # expired rating
                
                i.rated_submission = None
                i.current_rating = None
                i.save()
                
            else:
                
                if i.rated_submission == None:
                    print >> sys.stdout, "Warning: evaluation found rating that wasn't saved for %s!" % i
            
update_institution_properties()