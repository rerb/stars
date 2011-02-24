from stars.apps.submissions.models import *
from stars.apps.tool.my_submission.views import init_credit_submissions

def migrate_submission(old_ss, new_cs):
    """
        migrate a submissionset `old_ss` from it's current creditset to `new_cs`
        
            - old_ss is locked (if it isn't already)
            - New submissionset, new_ss is created for new_cs
            - Initialize the new_ss
            - Iterate through items in new_ss and migrate data from old_ss
            
        returns new SubmissionSet
    """
    
    # double checks:
        # status == 'ps'
        # deadline < today
        # ss.cs != new_cs
    
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
    
    # move payments
    for p in old_ss.payment_set.all():
        p.submissionset = new_ss
        p.save()
    
    # for testing, copy the payments
#    for p in old_ss.payment_set.all():
#        new_p = copy.copy(p)
#        new_p.id = None
#        new_p.submissionset = new_ss
#        new_p.save()
    
    # if the old SubmissionSet hasn't been initialized we don't have to do anything
    if old_ss.categorysubmission_set.count() == 0:
        new_ss.is_locked=False
        new_ss.is_visisble=True
        new_ss.save()
        return new_ss
    
    init_credit_submissions(new_ss)
    
    # Since there is currently no change necessary with the category we will ignore it
    #    for cat in new_ss.categorysubmission_set.all():
    #        try:
    #            old_cat = ss.categorysubmission_set.get(category=cat.category.previous_version)
    #        except CategorySubmission.DoesNotExist:
    #            continue
        
    # Get all SubcategorySubmissions in this SubmissionSet regardless of Category
    
    print new_ss
    
    for sub in SubcategorySubmission.objects.filter(category_submission__submissionset=new_ss):
        # Try to find a parent
        prev_sub = sub.subcategory.previous_version
        # if it has a previous version
        if prev_sub:
            try:
                old_sub = SubcategorySubmission.objects.get(category_submission__submissionset=old_ss, subcategory=prev_sub)
                sub.description = old_sub.description
                sub.save()
            except SubcategorySubmission.DoesNotExist:
                # This must be a new subcategory
                print "no old subcategory submission: %s" % sub.subcategory
                continue
        else:
            print "new subcategory: %s" % sub.subcategory
        
    for c in CreditUserSubmission.objects.filter(subcategory_submission__category_submission__submissionset=new_ss):
        # find the parent credit
        prev_credit = c.credit.previous_version
        
        print "%s - %s" % (c.credit, prev_credit)
        
        if prev_credit:
            try:
                old_c = CreditUserSubmission.objects.get(subcategory_submission__category_submission__submissionset=old_ss, credit=prev_credit)
                
                c.last_updated = old_c.last_updated
                c.user = old_c.user
                c.internal_notes = old_c.internal_notes
                c.submission_notes = old_c.submission_notes
                c.responsible_party = old_c.responsible_party
                
                if old_c.submission_status != 'ns':
                    c.submission_status = 'p'
                c.save()
                
            except CreditUserSubmission.DoesNotExist:
                print "no old credit submission: %s" % c.credit
                continue
            
            # get all the fields in this credit
            for f in c.get_submission_fields():
                
                prev_df = f.documentation_field.previous_version
                
                if prev_df:
                    field_class = f.__class__
                    try:
                        old_f = field_class.objects.get(documentation_field=prev_df, credit_submission=old_c)
                        f.value = old_f.value
                        f.save()
                        print "moved: %s" % f.documentation_field
                    except field_class.DoesNotExist:
#                        print "no old documentation field: %s" % f.documentation_field
                        continue
                    
                else:
                    print "No previous documentation field: %s" % f.documentation_field
                    continue
        else:
            print "new credit: %s" % c.credit
            continue
            
    new_ss.is_locked = False
    new_ss.is_visible = True
    
    new_ss.save()
    
    # make active submission set
    new_ss.institution.set_active_submission(new_ss)
    
    old_ss.is_visible = False
    old_ss.save()
    
    return new_ss
    
