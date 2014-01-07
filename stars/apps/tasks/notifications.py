"""
    Run daily to determine if any notifications need to be sent to
    institutions who haven't paid

    Institutions get a notification after 4 weeks indicating that they
    haven't paid.
"""

from datetime import timedelta, datetime, date
import sys, calendar

from stars.apps.institutions.models import * # required for execfile management func
from stars.apps.submissions.models import (Payment, 
                                           PENDING_SUBMISSION_STATUS,
                                           SubmissionSet)
from stars.apps.tasks.models import EmailNotification
from stars.apps.notifications.models import EmailTemplate

def get_new_institutions(current_date):
    """
        Return a list of all institutions that paid more than a week ago.
    """
    one_week = timedelta(weeks=1)
    date_limit = current_date - one_week

    i_list = []
    for p in Payment.objects.filter(date__lte=date_limit).exclude(type='later'):
        if (not p.submissionset.institution.charter_participant and
            p.submissionset.status == PENDING_SUBMISSION_STATUS):
            i_list.append(p.submissionset.institution)

    return i_list

def send_welcome_email(current_date=date.today()):
    """
        This is separated from `get_new_institutions` for testing purposes
    """

    for i in get_new_institutions(current_date):

        send_notification(
                            n_type='wel',
                            identifier="wel-%d" % i.id,
                            mail_to=[i.contact_email,],
                            template_slug="welcome_one_week",
                            email_context={'institution': i,}
                        )

def get_overdue_payments(weeks, current_date=date.today()):
    """
        Return a list of all submission sets that were registered
        more than `weeks` before the current and still have not paid
    """

    td = timedelta(weeks=weeks)
    date_limit = current_date - td

    ss_list = []
    for ss in SubmissionSet.objects.filter(date_registered__lte=date_limit).filter(is_visible=True).order_by('institution__name'):
        if ss.get_amount_due() > 0 and ss.institution.aashe_id != 15889: # don't send to CSB
            ss_list.append(ss)

    return ss_list

def send_overdue_notifications(current_time=datetime.now()):
    """
        This is separated from `get_overdue_contacts` for testing purposes
    """

    sent_list = []

    for ss in get_overdue_payments(8, current_time):

        email_context = {
                "amount_due": ss.get_amount_due(),
                "ss": ss
        }

        send_notification(
                            n_type='8wk',
                            identifier="8wk-%d" % ss.id,
                            mail_to=[ss.institution.contact_email,],
                            template_slug="overdue_payment",
                            email_context=email_context
                        )
        sent_list.append(ss)

    for ss in get_overdue_payments(4, current_time):

        if ss not in sent_list: # don't send twice.

            email_context = {
                    "amount_due": ss.get_amount_due(),
                    "ss": ss
            }

            send_notification(
                n_type='4wk',
                identifier="4wk-%d" % ss.id,
                mail_to=[ss.institution.contact_email,],
                template_slug="overdue_payment",
                email_context=email_context
                )


def send_renewal_reminder(current_date=date.today()):
    """
        Send one reminder immediately after a subscription expires
        and then another 60 days later (30 days before the discount expires)

        Don't send the email if they have renewed. This uses the is_participant
        field, which assumes that the subscription monitor is working
    """

    sub_list = Subscription.objects.filter(institution__is_participant=False)
    sub_list = sub_list.filter(institution__international=False)

    n_type = '30r'

    message_list = []

    for sub in sub_list:

        days_ago = current_date - sub.end_date

        if days_ago.days < 90 and days_ago.days >= 60:
            exp_date = sub.end_date + timedelta(days=90)
            m = {
                    'mail_to': [sub.institution.contact_email],
                    'template_slug': "renewal_thirty_days",
                    'email_context': {'sub': sub,
                                      'exp_date': exp_date},
                    'n_type': n_type,
                    'identifier': '%s-%d' % (n_type, sub.id)
                 }
            message_list.append(m)

    send_notification_set(message_list)


def send_post_submission_survey(current_date=None):
    """
        Gets the submission sets that were submitted 2 weeks or more ago
        current_date is optional for debugging

        Don't send if more than 60 days old
    """

    if not current_date:
        current_date = date.today()

    td_14 = current_date - timedelta(days=14)
    td_60 = current_date - timedelta(days=60)
    message_list = []

    qs = SubmissionSet.objects.filter(status='r')
    qs = qs.filter(date_submitted__lte=td_14)
    qs = qs.filter(date_submitted__gte=td_60)

    for ss in qs:

        print "Sending survey email for: %s (%s)" % (ss, ss.date_submitted)

        m = {
                'mail_to': [ss.institution.contact_email,],
                'template_slug': "post_submission_survey",
                'email_context': {'ss': ss,},
                'n_type': PENDING_SUBMISSION_STATUS,
                'identifier': 'ps-%d' % ss.id,
             }
        message_list.append(m)

    send_notification_set(message_list)

def send_notification_set(notification_set):
    """
        Sends a set of notifications
        set structure:
        (
            {'mail_to': [], 'message': '', 'n_type': '', 'identifier': '', 'subject': ''},
            ...
        )
    """

    for n in notification_set:
        send_notification(
                            n_type=n['n_type'],
                            identifier=n['identifier'],
                            mail_to=n['mail_to'],
                            template_slug=n['template_slug'],
                            email_context=n['email_context']
                        )

def add_months(d, months):
    """
        Returns a number of months after the given date
        negative months are ok
    """

    year = d.year
    month = d.month
    day = d.day

    month += months
    year += int(month) / int(12)
    month = int(month) % int(12)

    min_days, max_days = calendar.monthrange(year, month)
    if max_days < day:
        day = max_days

    return date(year=year, month=month, day=day)

def send_notification(n_type, identifier, mail_to, template_slug, email_context, count=1):
    """
        Send a notification of a particular type, identifier and mail_to
        If this notification has already been sent `count` times, ignore it.
    """

    if EmailNotification.objects.filter(identifier=identifier).count() < count:

        try:
            et = EmailTemplate.objects.get(slug=template_slug)
            et.send_email(mail_to, email_context)

            en = EmailNotification(identifier=identifier, notification_type=n_type, sent_to=mail_to, subject=et.title)
            en.save()
        except Exception, e:
            print >> sys.stderr, "Message Send Failed: %s (%s) [%s]" % (mail_to, template_slug, e)
