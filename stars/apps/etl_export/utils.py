from stars.apps.etl_export.models import Institution, SubmissionSet, Subscription, SubscriptionPayment, Boundary
        
def update_etl():
    
    SubmissionSet.etl_run_update()
    Institution.etl_run_update()
    Subscription.etl_run_update()
    SubscriptionPayment.etl_run_update()
    Boundary.etl_run_update()
    
