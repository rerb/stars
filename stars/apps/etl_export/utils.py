from stars.apps.etl_export.models import Institution, SubmissionSet, Subscription, SubscriptionPayment, Boundary
        
import sys

def update_etl():
    
    print >> sys.stdout, "Exporting SubmissionSets" 
    SubmissionSet.etl_run_update()
    print >> sys.stdout, "Exporting Institutions" 
    Institution.etl_run_update()
    print >> sys.stdout, "Exporting Subscriptions" 
    Subscription.etl_run_update()
    print >> sys.stdout, "Exporting Subscription payments" 
    SubscriptionPayment.etl_run_update()
    print >> sys.stdout, "Exporting Boundaries" 
    Boundary.etl_run_update()
    
