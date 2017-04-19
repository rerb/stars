import datetime

from stars.apps.institutions.models import Institution


def eval_participant_status(i):
    """
        Does the evaluation of participant status, instead of using
        the is_participant field

        returns (is_participant, current_subscription)
    """

    # see if there is a current subscription
    for sub in i.subscription_set.order_by('start_date'):
        # print sub
        if (
            sub.start_date <= datetime.date.today() and
            sub.end_date >= datetime.date.today()
        ):
            return (True, sub)

    return (False, None)


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

    for i in Institution.objects.all():

        is_participant, current_subscription = eval_participant_status(i)

        # if the current_subscription is over 30 days old, then mark as late
        thirty = datetime.timedelta(days=30)

        if current_subscription and not current_subscription.paid_in_full:
            if ((datetime.date.today() - thirty) >
                current_subscription.start_date):  # noqa

                current_subscription.late = True
                current_subscription.save()
                is_participant = False

        # Participation Status
        if i.is_participant != is_participant:
            """
                potential @bug - although might be desirable
                when there's an unpaid rollover subscription, the school will
                still get an expiration notice
            """

            # if participation status has changed

            if not i.is_participant:
                # renewal: wasn't and now is
                i.is_participant = True
                i.current_subscription = current_subscription
            else:
                # expiration: was and now isn't
                i.is_participant = False
                i.current_subscription = None
            i.save()

        else:

            # check if there's a rollover subscription
            if i.current_subscription != current_subscription:
                i.current_subscription = current_subscription
                i.save()

        # Rating
        try:
            rated_submission = i.submissionset_set.filter(status='r').order_by(
                '-date_submitted')[0]
        except IndexError:
            rated_submission = None

        if i.rated_submission != rated_submission and rated_submission is None:
            # expired rating
            i.rated_submission = None
            i.current_rating = None
            i.save()
