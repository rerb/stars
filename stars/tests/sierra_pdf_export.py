"""
    PDF Report Generation
"""
import sys, os
import datetime

from django.conf import settings

from stars.apps.institutions.models import *
from stars.apps.submissions.models import SubmissionSet
from stars.apps.third_parties.models import ThirdParty

def pdf_export():
    
    d = datetime.date(month=6, day=12, year=2012)
    
    tp = ThirdParty.objects.get(pk=2)
    
    skip_list = []

    for ss in tp.get_snapshots().filter(date_submitted__lte=d).order_by('institution__name', "-date_submitted"):
        print "%s - %s" % (ss.institution, ss.date_submitted)
        if ss.institution.id in skip_list:
            print "skipped"
        else:
            skip_list.append(ss.institution.id)
#            ss = SubmissionSet.objects.get(pk=v)
#            outfile = "stars_snapshot_%s.pdf" % k
            outfile = "pdfs/%s" % ss.get_pdf_filename()
            
            pdf = ss.get_pdf(False, template='institutions/pdf/third_party_report.html')
    #        path = os.path.join(settings.PROJECT_PATH,) # the stars directory
            f = open(outfile, 'w')
            f.write(pdf)
        
if __name__ == "__main__":
    pdf_export()
        
    #        pdf = pisa.CreatePDF(html, file(outfile, "wb"), path)
    
    #    f = open('stars_report.html', 'w')
    #    f.write(smart_str(html))