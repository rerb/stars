#!/usr/bin/env python

from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.tasks import send_certificate_pdf

from django.conf import settings

import sys

ss_id_list = [
    283, 430
]

settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
settings.CELERY_ALWAYS_EAGER = True

for ss_id in ss_id_list:
    ss = SubmissionSet.objects.get(pk=ss_id)
    print >> sys.stdout, "Running cert for %s" % ss
    send_certificate_pdf.delay(ss)
    print >> sys.stdout, "Done"
