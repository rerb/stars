import django.dispatch
from django.db.models.signals import pre_save
from django.dispatch import receiver

from stars.apps.institutions import Institution, Subscription, SubscriptionPayment
from stars.apps.helpers import logger

logger = logger.getLogger(__name__)

@receiver(post_save, sender=SubscriptionPayment)
def apply_payment(sender, **kwargs):
    """
        When a payment is saved, apply the changes to the subscription
        and institution

        if it's a new payment then add all the payments up for that
        subscription and mark paid_in_full if necessary
    """
    payment = kwargs['instance']
    subscription = payment.subscription
    total = 0
    for p in subscription.subscriptionpayment_set.all():
        total += p.amount
    if total == subscription.amount_due:
        subscription.paid_in_full = True
    elif total < subscription.amount_due:
        subscription.paid_in_full = False
    else:
        logger.error("Payments exceed amount due for %s." %
                     subscription.institution, {'who': 'apply_payment'})
    subscription.institution.update_status()

"""
Events:

    Registration
        - add subscription
        - update status
        - add submission
        - set current_submission, current_subscription
        - trigger email
        STEPS
            1. Select Institution
            2. Add Contact Info
            3. Select Level of participation
            4. Pay
            5. Create Institution
            6. Initialize participation
    Free Registration
        - add submission
        - set current_submission
        - trigger email
        STEPS
            1. Select Institution
            2. Add Contact Info
            3. Select Level of participation
            4. Save Institution
            5. Initialize participation
    Subscription Purchase
        - add subscription
        - update status
        - trigger email
    Subscription Ends
        - update status
        - clear current_subscription
        - trigger email
    Submission for Rating
        - add submission
        - migrate submission data
        - add subscription
        - set current_subscription
        - update current_rating, rated_submission, rating_expires
        - trigger email
    Rating Expires
        - update current_rating, rated_submission, rating_expires
        - trigger email
    Migrate STARS Version
        - add submission
        - migrate data
        - delete old submission
        - update current_submission
"""
