#!/usr/bin/env python

from stars.apps.institutions.models import *
from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.pdf.export import build_certificate_pdfs

outfile = "certificate.pdf"

ss = SubmissionSet.objects.get(pk=60)
pdf = build_certificate_pdfs(SubmissionSet.objects.filter(status='r'))
f = open(outfile, 'w')
f.write(pdf.getvalue())