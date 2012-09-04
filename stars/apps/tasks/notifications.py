"""
    Run daily to determine if any notifications need to be sent to institutions who haven't paid
    Institutions get a notification after 4 weeks indicating that they haven't paid.
"""

from datetime import timedelta, datetime, date
import sys, calendar

from stars.apps.institutions.models import * # required for execfile management func
from stars.apps.submissions.models import SubmissionSet, Payment
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
        if not p.submissionset.institution.charter_participant and p.submissionset.status == 'ps':
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
        Remind institutions that they have 30 days to renew keep their registration discounts

        Institutions have 90 days to renew

        Limit institutions:

            - Submitted more than 60 days ago and less than 90 (expired)
            OR
            - Submitted before 1/31/11 after 4/1/11
    """

    # submissions more than 60 days old and less than 90
    jan_thirty_one = date(year=2011, month=1, day=31)
    sixty_days_ago = current_date - timedelta(days=60)
    ninety_days_ago = current_date - timedelta(days=90)

    ss_list = SubmissionSet.objects.filter(status='r')
    ss_list = ss_list.filter(date_submitted__gte=jan_thirty_one) # exclude early submissions
    ss_list = ss_list.filter(date_submitted__lte=sixty_days_ago)
    ss_list = ss_list.filter(date_submitted__gte=ninety_days_ago)

    # submission before 1/31/11
    # if it's after 4/1/11 and before 5/1/11
    # (the end date isn't super significant, since it only gets sent once)
    if current_date > date(year=2011, month=4, day=1) and current_date < date(year=2011, month=5, day=1):
        ss_list = ss_list |  SubmissionSet.objects.filter(status='r').filter(date_submitted__lte=jan_thirty_one)

    n_type = '30renew'
    identifier = '30renew'

    message_list = []

    for ss in ss_list:

        m = {
                'mail_to': [ss.institution.contact_email,],
                'template_slug': "renewal_thirty_days",
                'email_context': {'ss': ss,},
                'n_type': 'rn',
                'identifier': 'rn-%d' % ss.id,
             }
        message_list.append(m)

    send_notification_set(message_list)

def send_post_submission_survey(current_date=None):
    """
        Gets the submission sets that were submitted 30 days or more ago
        current_date is optional for debugging
    """

    if not current_date:
        current_date = date.today()

    d = current_date - timedelta(days=30)
    message_list = []

    for ss in SubmissionSet.objects.filter(date_submitted__lte=d).filter(status='r'):

        m = {
                'mail_to': [ss.institution.contact_email,],
                'template_slug': "post_submission_survey",
                'email_context': {'ss': ss,},
                'n_type': 'ps',
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
