"""
    Celery tasks
"""
from stars.apps.submissions.pdf.export import build_certificate_pdf
from stars.apps.submissions.utils import migrate_submission
from stars.apps.notifications.models import EmailTemplate
from stars.apps.helpers import watchdog

from django.core.mail import EmailMessage, get_connection
from django.conf import settings

from celery.decorators import task

import sys

@task()
def send_certificate_pdf(ss):
    
    pdf = build_certificate_pdf(ss)

    m = EmailMessage(
                        subject="New Certificate: %s" % ss,
                        body="%s submitted" % ss.institution,
                        to=['marnie@aashe.org',],
                        bcc=['ben@aashe.org',],
                        headers = {'Reply-To': 'stars@aashe.org'},
                        attachments = ((ss.institution.slug, pdf.getvalue(), 'application/pdf'),),
                    )
    m.send()
    
@task()
def perform_migration(old_ss, new_cs, user):
    """
        Run the migration and then
        email the Liaison, copying the user
        (if the emails are different)
    """
    
    new_ss = migrate_submission(old_ss, new_cs)
    
    email_to = [old_ss.institution.contact_email]
    if user.email not in email_to:
        email_to.append(user.email)
        
    try:
        et = EmailTemplate.objects.get(slug='migration_success')
        email_context = {"old_ss": old_ss, "new_ss": new_ss}
        et.send_email(email_to, email_context)
        
    except EmailTemplate.DoesNotExist:
        watchdog.log('perform_migration', 'Migration email template missing', watchdog.ERROR)
    