from stars.apps.submissions.models import CreditUserSubmission, SubmissionSet
from stars.apps.credits.models import Credit

print """
    This tool will change the status of a credit user submission and update
    the score and rating for their overall submission.
    
    Use quotes for the new status, like 'np' in your input.
"""

credit_id = input('Credit ID: ')
submissionset_id = input('SubmissionSet ID: ')
new_status = str(input('New Status: '))

ss = SubmissionSet.objects.get(pk=submissionset_id)
credit = Credit.objects.get(pk=credit_id)

cus = CreditUserSubmission.objects.get(credit=credit, subcategory_submission__category_submission__submissionset=ss)

print ss
print "Changing Status for %s from %s to %s" % (cus, cus.submission_status, new_status)

cus.submission_status = new_status

if cus.assessed_points != cus._calculate_points():
    cus.assessed_points = cus._calculate_points()
    cus.save()
    
    cus.subcategory_submission.points = None
    cus.subcategory_submission.points = cus.subcategory_submission.get_claimed_points()
    cus.subcategory_submission.save()
    
    cus.subcategory_submission.category_submission.score = None
    cus.subcategory_submission.category_submission.score = cus.subcategory_submission.category_submission.get_STARS_score()
    cus.subcategory_submission.category_submission.save()
    
    print "score changed from %s" % ss.score
    ss.score = None
    ss.score = ss.get_STARS_score()
    print "to %s" % ss.score
    ss.save()
    
    new_rating = ss.get_STARS_rating(recalculate=True)
    if ss.rating != new_rating:
        print "Rating Changed from %s to %s!" % (ss.rating, new_rating)
        ss.rating = new_rating
        rating_changed = True
        ss.save()

ss.pdf_report = None
ss.save()