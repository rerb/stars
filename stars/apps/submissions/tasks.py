"""
    Celery tasks
"""
from stars.apps.submissions.pdf.export import build_certificate_pdf
from stars.apps.submissions.utils import migrate_ss_version, migrate_submission
from stars.apps.notifications.models import EmailTemplate
from stars.apps.helpers import watchdog

from django.core.mail import EmailMessage, get_connection
from django.conf import settings

from celery.decorators import task

import sys

@task()
def hello_world():
    " A simple test task so I can test celery "
    print >> sys.stdout, "Hello World"

@task()
def send_certificate_pdf(ss):
    
    pdf = build_certificate_pdf(ss)

    et = EmailTemplate.objects.get(slug='certificate_to_marnie')
    email_context = {"ss": ss}
    et.send_email(
                    mail_to=['marnie@aashe.org',],
                    context=email_context,
                    attachments=((ss.institution.slug, pdf.getvalue(), 'application/pdf'),),
                    title="New Certificate: %s" % ss)
    
@task()
def perform_migration(old_ss, new_cs, user):
    """
        Run the migration and then
        email the Liaison, copying the user
        (if the emails are different)
    """
    
    new_ss = migrate_ss_version(old_ss, new_cs)
    
    email_to = [old_ss.institution.contact_email]
    if user.email not in email_to:
        email_to.append(user.email)
        
    try:
        et = EmailTemplate.objects.get(slug='migration_success')
        email_context = {"old_ss": old_ss, "new_ss": new_ss}
        et.send_email(email_to, email_context)
        
    except EmailTemplate.DoesNotExist:
        watchdog.log('perform_migration', 'Migration email template missing', watchdog.ERROR)

@task()
def migrate_purchased_submission(old_ss, new_ss):
    """
        Hide the submission, move the data from the old_ss
        and then unhide it
    """
    new_ss.is_visible = False
    new_ss.is_locked = True
    new_ss.save()
    
    migrate_submission(old_ss, new_ss)
    
    new_ss.is_visible = True
    new_ss.is_locked = False
    new_ss.save()