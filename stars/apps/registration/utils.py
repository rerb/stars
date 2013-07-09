from stars.apps.institutions.models import Subscription, StarsAccount
from stars.apps.submissions.models import SubmissionSet
from stars.apps.credits.models import CreditSet

import re
from datetime import date, timedelta


def init_starsaccount(user, institution):
    """
        Add a StarsAccount to institution for user with the admin permission
    """
    account = StarsAccount(user=user, institution=institution,
                           user_level='admin', is_selected=False,
                           terms_of_service=True)
    account.save()
    account.select()
    return account


def init_submissionset(institution, user, date_callback=date.today):
    """
        Initializes a submissionset for an institution and user
        adding the today argument makes this easier to test explicitly
    """
    # Get the current CreditSet
    creditset = CreditSet.objects.get_latest()
    # Submission is due in one year
    submissionset = SubmissionSet(creditset=creditset,
                                  institution=institution,
                                  date_registered=date_callback(),
                                  registering_user=user, status='ps')
    submissionset.save()
    institution.current_submission = submissionset
    institution.save()
    return submissionset


def init_subscription(institution, amount_due, date_callback=date.today):
    """
        Initializes a subscription for the institution with the payment

        @todo: use a signal to update the subscription amount_due and paid_in_full
    """
    deadline = date_callback() + timedelta(days=365) # Gives them an extra day on leap years :)
    subscription = Subscription(
                                institution=institution,
                                start_date=date_callback(),
                                end_date=deadline,
                                amount_due=amount_due,
                                paid_in_full=(amount_due==0))
    if institution.international:
        subscription.reason = "international"
    elif institution.is_member:
        subscription.reason = "member_reg"
    else:
        subscription.reason = "nonmember_reg"
    subscription.save()
    return subscription
