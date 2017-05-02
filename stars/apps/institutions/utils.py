import datetime

from stars.apps.institutions.models import Institution


def get_current_subscription(institution):

    today = datetime.date.today()

    try:
        current_subscription = institution.subscription_set.filter(
            start_date__lte=today,
            end_date__gte=today).order_by("start_date")[0]
    except IndexError:
        current_subscription = None

    return current_subscription


def update_institution_properties(institution):
    """Update one Institution's properties.

        Updates the following properties:

            current_subscription
            current_rating, rated_submission

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
    institution.current_subscription = get_current_subscription(institution)

    # Rating
    try:
        rated_submission = institution.submissionset_set.filter(
            status='r').order_by(
                '-date_submitted')[0]
    except IndexError:
        rated_submission = None

    institution.rated_submission = (rated_submission
                                    if rated_submission
                                    else None)

    institution.current_rating = (rated_submission.rating
                                  if institution.rated_submission
                                  else None)

    institution.save()


def update_all_institution_properties():
    """Update properties for all Institutions.
    """
    for institution in Institution.objects.all():
        update_institution_properties(institution=institution)
