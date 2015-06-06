from stars.apps.institutions.models import StarsAccount
from stars.apps.submissions.models import (PENDING_SUBMISSION_STATUS,
                                           SubmissionSet)
from stars.apps.credits.models import CreditSet

from datetime import date


def init_starsaccount(user, institution):
    """
        Add a StarsAccount to institution for user with the admin permission.
    """
    account = StarsAccount(user=user, institution=institution,
                           user_level='admin', is_selected=False,
                           terms_of_service=True)
    account.save()
    account.select()
    return account


def init_submissionset(institution, user, date_function=date.today):
    """
        Initializes a submissionset for an institution and user.
    """
    # Get the current CreditSet
    creditset = CreditSet.objects.get_latest()
    # Submission is due in one year
    submissionset = SubmissionSet(creditset=creditset,
                                  institution=institution,
                                  date_registered=date_function(),
                                  registering_user=user,
                                  status=PENDING_SUBMISSION_STATUS)
    submissionset.save()
    institution.current_submission = submissionset
    institution.save()
    return submissionset
