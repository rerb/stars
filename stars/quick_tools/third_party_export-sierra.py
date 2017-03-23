#!/usr/bin/env python

"""
    Tool to export snapshots for Sierra.
"""
import datetime
import os
import string

from stars.apps.credits.models import CreditSet
from stars.apps.third_parties.models import ThirdParty
from stars.apps.third_parties.utils import export_credit_csv


limit_inst_ids = [
    # if this has ids, then only these institutions will be exported
]

credit_sets = [CreditSet.objects.get(version=2.0),
               CreditSet.objects.get(version=2.1)]


for cs in credit_sets:

    tp = ThirdParty.objects.get(slug="sierra")
    print "EXPORTING: %s" % tp

    start_date = datetime.date(year=2016, month=3, day=4)
    end_date = datetime.date(year=2017, month=3, day=13)

    snapshot_list = tp.get_snapshots().order_by("institution__name")
    snapshot_list = snapshot_list.filter(creditset=cs)
    snapshot_list = snapshot_list.filter(date_submitted__gte=start_date)
    snapshot_list = snapshot_list.filter(date_submitted__lte=end_date)

    if(limit_inst_ids):
        snapshot_list = snapshot_list.filter(
            institution__id__in=limit_inst_ids)

    inst_list = []
    latest_snapshot_list = []  # only use the latest snapshot
    for ss in snapshot_list:
        if ss.institution.id not in inst_list:
            inst_list.append(ss.institution.id)
            i_ss_list = ss.institution.submissionset_set.filter(
                status='f').order_by('-date_submitted', '-id').filter(
                    date_submitted__gte=start_date).filter(
                        date_submitted__lte=end_date)
            print "Available snapshots for %s" % ss.institution
            for __ss in i_ss_list:
                print "%s, %d" % (__ss.date_submitted, __ss.id)
            if i_ss_list[0].creditset == cs:
                latest_snapshot_list.append(i_ss_list[0])
            else:
                print "newer snapshot in version: %s" % i_ss_list[0].creditset
            print "Selected snapshot:%s, %d" % (
                i_ss_list[0].date_submitted, i_ss_list[0].id)

    for cat in cs.category_set.all():
        for sub in cat.subcategory_set.all():
            for c in sub.credit_set.all():
                filename = 'sierra/export/%s/%s.csv' % (
                    cs.version, string.replace("%s" % c, "/", "-"))
                filename = string.replace(filename, ":", "")
                filename = string.replace(filename, " ", "_")

                export_credit_csv(c,
                                  ss_qs=latest_snapshot_list,
                                  outfilename=filename)

    # export pdfs
    count = 0
    total = len(latest_snapshot_list)
    pdf_path = "./sierra/export/pdf"
    if not os.path.exists(pdf_path):
        os.makedirs(pdf_path)
    for ss in latest_snapshot_list:
        count += 1
        print ss
        print "%d of %d" % (count, total)
        outfile = os.path.join(pdf_path, ss.get_pdf_filename())
        pdf = ss.get_pdf(refresh=False,
                         template='institutions/pdf/third_party_report.html')
        os.rename(pdf, outfile)
