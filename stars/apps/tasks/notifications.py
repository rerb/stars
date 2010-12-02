"""
    Run daily to determine if any notifications need to be sent to institutions who haven't paid
    Institutions get a notification after 4 weeks indicating that they haven't paid.
    
    @Todo: other notifications include 6 months and 1 month before submission deadline
"""

from datetime import timedelta, datetime, date
import sys, calendar

from django.template import Context, loader, Template
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage

from stars.apps.institutions.models import * # required for execfile management func
from stars.apps.submissions.models import SubmissionSet, Payment
from stars.apps.tasks.models import EmailNotification

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

def send_welcome_email(current_date):
    """
        This is separated from `get_new_institutions` for testing purposes
    """
    
    for i in get_new_institutions(current_date):

        t = loader.get_template('tasks/notifications/welcome.txt')
        c = Context({'institution': i,})
        message = t.render(c)
    
        send_notification(
                            n_type='wel',
                            identifier="wel-%d" % i.id,
                            mail_to=[i.contact_email,],
                            message=message,
                            subject="Welcome to STARS",
                        )

def get_overdue_payments(current_date):
    """
        Return a list of all submission sets that were registered
        more than 4 weeks before the current and still have not paid
    """
    
    four_weeks = timedelta(weeks=4)
    date_limit = current_date - four_weeks
    
    ss_list = []
    for ss in SubmissionSet.objects.filter(date_registered__lte=date_limit).order_by('institution__name'):
        if ss.payment_set.exclude(type='later').count() == 0 and ss.institution.aashe_id != 15889: # don't send to CSB
            ss_list.append(ss)
            
    return ss_list

def send_overdue_notifications(current_time):
    """
        This is separated from `get_overdue_contacts` for testing purposes
    """
    
    for ss in get_overdue_payments(current_time):

        t = loader.get_template('tasks/notifications/overdue.txt')
        c = Context({'ss': ss,})
        message = t.render(c)
    
        send_notification(
                            n_type='4wk',
                            identifier="4wk-%d" % ss.id,
                            mail_to=[ss.institution.contact_email,'margueritte.williams@aashe.org', 'allison@aashe.org'],
                            message=message,
                            subject="Reminder:  STARS Registration Fee Overdue",
                        )
                        
def get_six_month_sets(current_date):
    """
        Gets the submission sets that are due in six months or less
    """
    
    ss_list = []
    d = add_months(current_date, 6)
    for ss in SubmissionSet.objects.filter(submission_deadline__lte=d).filter(status='ps'):
        ss_list.append(ss)
    return ss_list
    
def send_six_month_notifications(current_time):
    """
        Remind institutions that they have 6 months before their submission is due
    """
    
    for ss in get_six_month_sets(current_time):

        t = loader.get_template('tasks/notifications/six_months.txt')
        c = Context({'ss': ss,})
        message = t.render(c)
    
        send_notification(
                            n_type='6mn',
                            identifier="six-%d" % ss.id,
                            mail_to=[ss.institution.contact_email,],
                            message=message,
                            subject="Reminder:  STARS Submission Due in 6 Months!",
                        )

def send_sixty_day_notifications(current_date=None):
    """
        Gets the submission sets that are due in sixty days or less
        current_date is optional for debugging
    """
    
    if not current_date:
        current_date = date.today()
        
    t = loader.get_template('tasks/notifications/sixty_days.txt')
    
    d = current_date + timedelta(days=60)
    message_list = []
    
    for ss in SubmissionSet.objects.filter(submission_deadline__lte=d):
        if ss.can_apply_for_extension(current_date):
            c = Context({'ss': ss,})
            
            m = {
                    'mail_to': [ss.institution.contact_email,],
                    'message': t.render(c),
                    'n_type': '60d',
                    'identifier': '60-%d' % ss.id,
                    'subject': 'STARS Submission: Due in 60 Days',
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
        
    t = loader.get_template('tasks/notifications/post_submission_survey.txt')
    
    d = current_date - timedelta(days=30)
    message_list = []
    
    for ss in SubmissionSet.objects.filter(date_submitted__lte=d).filter(status='r'):
        
        c = Context({'ss': ss,})
        m = {
                'mail_to': [ss.institution.contact_email,],
                'message': t.render(c),
                'n_type': 'ps',
                'identifier': 'ps-%d' % ss.id,
                'subject': 'STARS Post Submission Survey',
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
                            message=n['message'],
                            subject=n['subject'],
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
    
def send_notification(n_type, identifier, mail_to, message, subject, count=1):
    """
        Send a notification of a particular type, identifier and mail_to
        If this notification has already been sent `count` times, ignore it.
    """
    
    if EmailNotification.objects.filter(identifier=identifier).count() < count:
        
        try:
            m = EmailMessage(
                            subject=subject,
                            body=message,
                            to=mail_to,
                            bcc=['ben@aashe.org',],
                            headers = {'Reply-To': 'stars@aashe.org'},
                        )
            m.send()
            
            en = EmailNotification(identifier=identifier, notification_type=n_type, sent_to=mail_to, subject=subject)
            en.save()
        except Exception, e:
            print >> sys.stderr, "Message Send Failed: %s (%s) [%s]" % (mail_to, subject, e)
            
