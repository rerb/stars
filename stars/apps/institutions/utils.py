import datetime

from stars.apps.institutions.models import Institution, FULL_ACCESS


def update_one_institutions_properties(institution):

    for sub in institution.subscription_set.order_by('start_date'):
        if (sub.start_date <= datetime.date.today() and
            sub.end_date >= datetime.date.today()):  # noqa

            current_subscription = sub
            is_participant = sub.access_level == FULL_ACCESS
            break
    else:
        current_subscription = None
        is_participant = False

    # if the current_subscription is over 30 days old, then mark as late
    thirty = datetime.timedelta(days=30)

    if current_subscription and not current_subscription.paid_in_full:
        if ((datetime.date.today() - thirty) >
            current_subscription.start_date):  # noqa

            current_subscription.late = True
            current_subscription.save()
            is_participant = False

    # Participation Status
    if institution.is_participant != is_participant:
        """
            potential @bug - although might be desirable
            when there's an unpaid rollover subscription, the school will
            still get an expiration notice
        """

        # if participation status has changed

        if not institution.is_participant:
            # renewal: wasn't and now is
            institution.is_participant = True
            institution.current_subscription = current_subscription
        else:
            # expiration: was and now isn't
            institution.is_participant = False
            institution.current_subscription = None
        institution.save()

    else:

        # check if there's a rollover subscription
        if institution.current_subscription != current_subscription:
            institution.current_subscription = current_subscription
            institution.save()

    # Rating
    try:
        rated_submission = institution.submissionset_set.filter(
            status='r').order_by(
            '-date_submitted')[0]
    except IndexError:
        rated_submission = None

    if (institution.rated_submission != rated_submission and
        rated_submission is None):  # noqa

        # expired rating
        institution.rated_submission = None
        institution.current_rating = None
        institution.save()


def update_institution_properties():
    """
        Nightly cron to maintain institution properties:
            is_participant
            current_subscription
            current_rating, rated_submission

            evaluate is_participant
            evaluate current_subscription
            evaluate current_rating

            compare with existing values

            if changed:
                check for subscription expiration
                    send email
                    create empty submission
                check for rating expiration
                    send email
    """
    for institution in Institution.objects.all():
        update_one_institutions_properties(institution=institution)
