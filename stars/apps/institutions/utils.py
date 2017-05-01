import datetime

from stars.apps.institutions.models import Institution


def deduce_current_subscription(institution):

    try:
        current_subscription = institution.subscription_set.filter(
            start_date__lte=datetime.date.today(),
            end_date__gte=datetime.date.today()).order_by('start_date')[0]
    except IndexError:
        current_subscription = None

    return current_subscription


def deduce_is_participant(institution):

    current_sub = institution.current_subscription

    if current_sub:
        return current_sub.access_level == current_sub.FULL_ACCESS
    else:
        return False


def update_institution_properties(institution):
    """Update one Institution's properties.

        Updates the following properties:

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
    institution.current_subscription = deduce_current_subscription(
        institution)
    institution.is_participant = deduce_is_participant(institution)

    # if the current_subscription is over 30 days old, then mark as late
    thirty = datetime.timedelta(days=30)

    if (institution.current_subscription and
        not institution.current_subscription.paid_in_full):  # noqa

        if ((datetime.date.today() - thirty) >
            institution.current_subscription.start_date):  # noqa

            institution.current_subscription.late = True
            institution.current_subscription.save()

    # Rating
    try:
        rated_submission = institution.submissionset_set.filter(
            status='r').order_by(
            '-date_submitted')[0]
    except IndexError:
        rated_submission = None

    institution.rated_submission = (
        rated_submission if rated_submission is not None else None)

    institution.current_rating = (
        rated_submission.rating if institution.current_rating is not None
        else None)

    institution.save()


def update_all_institution_properties():
    """Update properties for all Institutions.
    """
    for institution in Institution.objects.all():
        update_institution_properties(institution=institution)
