"""
    Celery tasks
"""
from stars.apps.submissions.pdf.export import build_certificate_pdf

from django.core.mail import EmailMessage, get_connection
from django.conf import settings

from celery.decorators import task

import sys

@task()
def send_certificate_pdf(ss):
    # print >> sys.stdout, "Starting Cert PDF Email"
    pdf = build_certificate_pdf(ss)
    
    m = EmailMessage(
                        subject="New Certificate: %s" % ss,
                        body="%s submitted" % ss.institution,
                        to=['ben@aashe.org',],
                        # bcc=['ben@aashe.org',],
                        headers = {'Reply-To': 'stars@aashe.org'},
                        attachments = ((ss.institution.slug, pdf.getvalue(), 'application/pdf'),),
                        # using the smtp email even for testing
                        connection = get_connection('django.core.mail.backends.smtp.EmailBackend'),
                    )
    m.send()
    
    print >> sys.stdout, "Back: %s" % settings.EMAIL_BACKEND
    
    print >> sys.stdout, "Sent Cert PDF Email"