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