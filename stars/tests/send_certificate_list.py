#!/usr/bin/env python

from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.tasks import send_certificate_pdf

import sys

ss_id_list = [
    430, 139, 300, 266, 131, 100, 280, 61, 283, 53, 278, 277, 122, 281
]

for ss_id in ss_id_list:
    ss = SubmissionSet.objects.get(pk=ss_id)
    print >> sys.stdout, "Running cert for %s" % ss
    send_certificate_pdf.delay(ss)
    print >> sys.stdout, "Done"
