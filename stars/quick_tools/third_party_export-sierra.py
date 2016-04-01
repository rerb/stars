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

cs_id_list = [6]
limit_inst_ids = [
    # if this has ids, then only these institutions will be exported
]

# institution_name_list = [
#     "American University",
#     "Ball State University",
#     "Bryant University",
#     "California State University, Monterey Bay",
#     "Central Connecticut State University",
#     "Denison University",
#     "Goucher College",
#     "Mills College",
#     "Randolph College",
#     "State University of New York at Oneonta",
#     "The Ohio State University",
#     "University at Albany",
#     "University of California, Merced",
#     "University of Michigan",
#     "University of North Texas",
#     "University of Richmond",
#     "Wellesley College"
# ]
#
# print "# of institutions: %d" % len(institution_name_list)
#
# for i_name in institution_name_list:
#     i = Institution.objects.get(name=i_name)
#     limit_inst_ids.append(i.id)
#
# print "# of institution ids: %d" % len(limit_inst_ids)


for cs_id in cs_id_list:

    cs = CreditSet.objects.get(pk=cs_id)
    tp = ThirdParty.objects.get(slug="sierra")
    print "EXPORTING: %s" % tp

    start = datetime.date(year=2015, month=3, day=31)
    deadline = datetime.date(year=2016, month=3, day=31)

    snapshot_list = tp.get_snapshots().exclude(institution__id=447).order_by("institution__name")
    snapshot_list = snapshot_list.filter(creditset=cs)
    snapshot_list = snapshot_list.filter(date_submitted__lte=deadline)
    snapshot_list = snapshot_list.filter(date_submitted__gte=start)

    if(limit_inst_ids):
        snapshot_list = snapshot_list.filter(institution__id__in=limit_inst_ids)

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

    # # export pdfs
    # count = 0
    # total = len(latest_snapshot_list)
    # for ss in latest_snapshot_list:
    #     count += 1
    #     print ss
    #     print "%d of %d" % (count, total)
    #     if count < 80:
    #         continue
    #     outfile = "export/pdf/%s" % ss.get_pdf_filename()
    #     # pdf = ss.get_pdf(False)
    #     # f = open(outfile, 'w')
    #     # f.write(pdf)
    #     pdf = ss.get_pdf(refresh=False, template='institutions/pdf/third_party_report.html')
    #     os.rename(pdf, outfile)
