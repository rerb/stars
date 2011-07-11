from stars.apps.etl_export.models import Institution, SubmissionSet, Payment
        
def update_etl():
    
    Institution.etl_run_update()
    SubmissionSet.etl_run_update()
    Payment.etl_run_update()
        
        
