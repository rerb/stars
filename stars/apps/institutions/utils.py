import datetime
import sys

from stars.apps.institutions.models import Institution
from stars.apps.notifications.models import EmailTemplate
from stars.apps.submissions.models import SubmissionSet


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


def eval_rated_submission(i):
    """
        Get the latest rated submission set for an institution

        @todo test chronological order
    """

    try:
        return i.submissionset_set.filter(status='r').order_by(
            '-date_submitted')[0]
    except:
        return None


def expire_ratings():
    """
        Expire any ratings that are over 3 years old
    """
    d = datetime.date.today()
    expire_date = d - datetime.timedelta(days=365*3)
    print "** Expiring Ratings **"
    for ss in SubmissionSet.objects.filter(date_submitted__lt=expire_date):
        ss.expired = True
        ss.save()
        print "Rating expired for %s (%s)" % (ss, ss.date_submitted)
        # remove it if it's the current submission for an institution
        if ss.institution.rated_submission == ss:
            ss.institution.rated_submission = None
            ss.institution.current_rating = None
            ss.institution.latest_expired_submission = ss
            ss.institution.save()
        else:
            print "Not their current rating"


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
            if (datetime.date.today() - thirty) > current_subscription.start_date:
                current_subscription.late = True
                current_subscription.save()
                is_participant = False
                print >> sys.stdout, "Late payment: %s" % current_subscription

        rated_submission = eval_rated_submission(i)

        # Participation Status

        if i.is_participant != is_participant:
            """
                potential @bug - although might be desirable
                when there's an unpaid rollover subscription, the school will
                still get an expiration notice
            """

            # if participation status has changed

            if not i.is_participant:
                # renewal: wasn't an now is
                i.is_participant = True
                if i.current_subscription:
                    print "Inconsistent status w/ subscription for %s" % i
                i.current_subscription = current_subscription
                print "Found subscription for %s" % i
            else:
                # expiration: was an now isn't
                i.is_participant = False
                i.current_subscription = None
                print "**********"
                print >> sys.stdout, "%s subscription expired" % i
                print "sending expiration notice to %s" % i.contact_email
                for sub in i.subscription_set.order_by('start_date'):
                    print "%s - %s" % (sub.start_date, sub.end_date)
                print "**********"
                # @todo email institution
                et = EmailTemplate.objects.get(
                    slug='stars_subscription_expired')
                et.send_email([i.contact_email], {'institution': i})
            i.save()

        else:

            # check if there's a rollover subscription
            if i.current_subscription != current_subscription:
                i.current_subscription = current_subscription
                print >> sys.stdout, "%s had a rollover subscription" % i
                i.save()

        # Rating

        if i.rated_submission != rated_submission:

            if rated_submission is None:

                # expired rating

                i.rated_submission = None
                i.current_rating = None
                i.save()

            # else:
            #
            #     if i.rated_submission is None:
            #         print >> sys.stdout, "Warning: evaluation found rating that wasn't saved for %s!" % i
