from stars.apps.submissions.models import CategorySubmission, SubcategorySubmission, CreditUserSubmission

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