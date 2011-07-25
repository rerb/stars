from stars.apps.submissions.models import *

def init_credit_submissions(submissionset):
    """ 
        Initializes all CreditUserSubmissions in a SubmissionSet
    """
    # Build the category list if necessary
    #if submissionset.creditset.category_set.count() > submissionset.categorysubmission_set.count():
    for category in submissionset.creditset.category_set.all():
        try:
            categorysubmission = CategorySubmission.objects.get(category=category, submissionset=submissionset)
        except:
            categorysubmission = CategorySubmission(category=category, submissionset=submissionset)
            categorysubmission.save()

        # Create SubcategorySubmissions if necessary
        #if category.subcategory_set.count() > categorysubmission.subcategorysubmission_set.count():
        for subcategory in categorysubmission.category.subcategory_set.all():
            try:
                subcategorysubmission = SubcategorySubmission.objects.get(subcategory=subcategory, category_submission=categorysubmission)
            except SubcategorySubmission.DoesNotExist:
                subcategorysubmission = SubcategorySubmission(subcategory=subcategory, category_submission=categorysubmission)
                subcategorysubmission.save()
            
            # Create CreditUserSubmissions if necessary
            #if subcategory.credit_set.count() > subcategorysubmission.creditusersubmission_set.count():
            for credit in subcategory.credit_set.all():
                try:
                    creditsubmission = CreditUserSubmission.objects.get(credit=credit, subcategory_submission=subcategorysubmission)
                except CreditUserSubmission.DoesNotExist:
                    creditsubmission = CreditUserSubmission(credit=credit, subcategory_submission=subcategorysubmission)
                    creditsubmission.save()

def migrate_ss_version(old_ss, new_cs):
    """
        Migrate a SubmissionSet from one CreditSet version to another
        
        - Locks the old submission.
        - Creates the new hidden one
        - Migrates the data
        - Hides the old one
        - Unhides the new one and makes it active
        - Moves payments over to new submission
        - Returns the new submissionset
    """
    
    if not old_ss.is_locked:
        old_ss.is_locked = True
        old_ss.save()

    new_ss = SubmissionSet(
                            creditset=new_cs,
                            institution=old_ss.institution,
                            date_registered=old_ss.date_registered,
                            submission_deadline=old_ss.submission_deadline,
                            registering_user=old_ss.registering_user,
                            status='ps',
                            is_locked=True,
                            is_visible=False)
    new_ss.save()
    
    init_credit_submissions(new_ss)
    
    new_ss = migrate_submission(old_ss, new_ss)

    # move payments
    for p in old_ss.payment_set.all():
        p.submissionset = new_ss
        p.save()
    
    new_ss.is_locked = False
    new_ss.is_visible = True

    new_ss.save()

    # make active submission set
    new_ss.institution.set_active_submission(new_ss)

    old_ss.is_visible = False
    old_ss.save()
    
    return new_ss

def migrate_submission(old_ss, new_ss, keep_status=False):
    """
        Migrate data from one SubmissionSet to another
        
        The returned SubmissionSet is locked and hidden
        
        Keeping the status will keep the submission status the same
        and transfer all the properties UNLESS the submissionsets
        are of different versions.
    """
    
    # if the old SubmissionSet hasn't been initialized we don't have to do anything
    if old_ss.categorysubmission_set.count() == 0:
        new_ss.save()
        return new_ss
    
    # Since there is currently no change necessary with the category we will ignore it
    # I'm keeping this in here in case we add data to the CategorySubmission objects
    #    for cat in new_ss.categorysubmission_set.all():
    #        try:
    #            old_cat = ss.categorysubmission_set.get(category=cat.category.previous_version)
    #        except CategorySubmission.DoesNotExist:
    #            continue
        
    # Get all SubcategorySubmissions in this SubmissionSet regardless of Category
    
    for sub in SubcategorySubmission.objects.filter(category_submission__submissionset=new_ss):
        
        # get the related subcategory
        prev_sub = sub.subcategory.get_for_creditset(old_ss.creditset)
        # print "%s Previous Subcategory: %s" % (sub.subcategory, prev_sub)
        
        # if it has a previous version
        if prev_sub:
            try:
                old_sub = SubcategorySubmission.objects.get(category_submission__submissionset=old_ss, subcategory=prev_sub)
                sub.description = old_sub.description
                sub.save()
                # print "saved: %s" % sub
            except SubcategorySubmission.DoesNotExist:
                # This must be a new subcategory
                # print "no old subcategory submission: %s" % sub.subcategory
                continue
        else:
            # print "new subcategory: %s" % sub.subcategory
            pass
        
    # print "Total CUS's: %d" % CreditUserSubmission.objects.count()
    
    for c in CreditUserSubmission.objects.filter(subcategory_submission__category_submission__submissionset=new_ss):
        
       
        # find the parent credit
        prev_credit = c.credit.get_for_creditset(old_ss.creditset)
        # print "Previous Credit: %s" % prev_credit
        
        if prev_credit:
            try:
                old_c = CreditUserSubmission.objects.get(subcategory_submission__category_submission__submissionset=old_ss, credit=prev_credit)
                
                c.last_updated = old_c.last_updated
                c.user = old_c.user
                c.internal_notes = old_c.internal_notes
                c.submission_notes = old_c.submission_notes
                c.responsible_party = old_c.responsible_party
                
                # can only keep status if the 
                if keep_status and old_ss.creditset.version ==  new_ss.creditset.version:
                    c.submission_status = old_c.submission_status
                    c.responsible_party_confirm = old_c.responsible_party_confirm
                    c.applicability_reason = old_c.applicability_reason
                    c.assessed_points = old_c.assessed_points
                else:
                    c.submission_status = 'ns'
                    if old_c.submission_status != 'ns':
                        c.submission_status = 'p'
                c.save()
                
            except CreditUserSubmission.DoesNotExist:
                # print "no old credit submission: %s" % c.credit
                continue
            
            # get all the fields in this credit
            for f in c.get_submission_fields():
                
                prev_df = f.documentation_field.get_for_creditset(old_ss.creditset)
                # print prev_df
                
                if prev_df:
                    field_class = f.__class__
                    try:
                        old_f = field_class.objects.get(documentation_field=prev_df, credit_submission=old_c)
                        f.value = old_f.value
                        f.save()
                        # print "moved: %s" % f.documentation_field
                    except field_class.DoesNotExist:
                        # print "no old documentation field: %s" % f.documentation_field
                        continue
                    
                else:
                    # print "No previous documentation field: %s" % f.documentation_field
                    continue
        else:
            # print "new credit: %s" % c.credit
            continue
    
    return new_ss