from datetime import timedelta, datetime

from stars.apps.etl_export.models import ETL
from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import SubmissionSet

def populate_etl_entry(institution):
    """
        Returns an ETL entry for a select institution
        This entry is not saved
    """
    
    # Init the new ETL object
    etl = ETL(aashe_id=institution.aashe_id, change_date=datetime.now())
    
    # Grab necessary data
    last_submission = institution.get_latest_submission(include_unrated=True)
    last_rated_submission = institution.get_latest_submission()
    active_submission = institution.get_active_submission()
    
    # Populate ETL object
    if last_submission:
        etl.participant_status = last_submission.get_status_display()
        etl.submission_due_date = last_submission.submission_deadline
        etl.registration_date = last_submission.date_registered
    if last_rated_submission:
        etl.current_rating = last_rated_submission.rating.name
        etl.rating_valid_until = last_rated_submission.date_submitted + timedelta(days=365*3)
        etl.last_submission_date = last_rated_submission.date_submitted
    if active_submission:
        etl.current_stars_version = active_submission.creditset.version
    elif last_submission:
        etl.current_stars_version = last_submission.creditset.version
    
    etl.liaison_first_name = institution.contact_first_name
    etl.liaison_middle_name = institution.contact_middle_name
    etl.liaison_last_name = institution.contact_last_name
    etl.liaison_title = institution.contact_title
    etl.liaison_department = institution.contact_department
    etl.liaison_phone = institution.contact_phone
    etl.liaison_email = institution.contact_email
    
    return etl

def update_etl_for_institution(i, etl):
    """
        This method populates the ETL list with updated status information
        Doctests are in tests/
    """
        
    new_etl = populate_etl_entry(i)
        
    if not etl:
        new_etl.save()
        print "Added New ETL: %s" % new_etl
        return new_etl
    
    elif etl != new_etl:
        etl.delete()
        new_etl.save()
        print "Updated ETL: %s" % new_etl
        return new_etl
    
    else:
        print "No Change: %s" % etl
        return etl
        
def update_etl():

    for i in Institution.objects.all():
        
        # See if an ETL object exists for this institution
        try:
            etl = ETL.objects.get(aashe_id=i.aashe_id)
        except ETL.DoesNotExist:
            etl = None
            
        etl = update_etl_for_institution(i, etl)
        
    # remove any extraneous institutions in ETL
    for etl in ETL.objects.all():
        try:
            i = Institution.objects.get(aashe_id=etl.aashe_id)
        except Institution.DoesNotExist:
            etl.delete()
        
        
        
