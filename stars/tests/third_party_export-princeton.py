#!/usr/bin/env python

"""
    Tool to export all content for a specific credit
"""

from stars.apps.institutions.models import *
from stars.apps.submissions.models import *
from stars.apps.credits.models import Credit
from stars.apps.third_parties.models import ThirdParty
from stars.apps.third_parties.utils import export_credit_csv

from django.utils.encoding import smart_unicode, smart_str

import csv, string
import datetime

cs_id_list = [5, 6]

for cs_id in cs_id_list:

    cs = CreditSet.objects.get(pk=cs_id)
    tp = ThirdParty.objects.get(slug="princeton")
    print "EXPORTING: %s" % tp

    deadline = datetime.date(year=2014, month=3, day=3)

    snapshot_list = tp.get_snapshots().exclude(institution__id=447).order_by("institution__name")
    snapshot_list = snapshot_list.filter(creditset=cs)
    snapshot_list = snapshot_list.filter(date_submitted__lte=deadline)

    # snapshot_list = snapshot_list | tp.get_snapshots().filter(id='1528')

    # latest_snapshot_list = tp.get_snapshots().filter(institution__id=267)

    inst_list = []
    latest_snapshot_list = [] # only use the latest snapshot
    for ss in snapshot_list:
        if ss.institution.id not in inst_list:
            inst_list.append(ss.institution.id)
            i_ss_list = ss.institution.submissionset_set.filter(status='f').order_by('-date_submitted', '-id').filter(date_submitted__lte=deadline)
            print "Available snapshots for %s" % ss.institution
            for __ss in i_ss_list:
                print "%s, %d" % (__ss.date_submitted, __ss.id)
            if i_ss_list[0].creditset == cs:
                latest_snapshot_list.append(i_ss_list[0])
            else:
                print "newer snapshot in version: %s" % i_ss_list[0].creditset
            print "Selected snapshot: %s, %d" % (i_ss_list[0].date_submitted, i_ss_list[0].id)

    print "%d Snapshots" % len(latest_snapshot_list)

    for cat in cs.category_set.all():
        for sub in cat.subcategory_set.all():
            for c in sub.credit_set.all():
                filename = 'export/%s/%s.csv' % (cs.version, string.replace("%s" % c, "/", "-"))
                filename = string.replace(filename, ":", "")
                filename = string.replace(filename, " ", "_")
             
                export_credit_csv(c, ss_qs=latest_snapshot_list, outfilename=filename)