"""
    PDF Report Generation
"""
import sys, os

from django.conf import settings

from stars.apps.institutions.models import *
from stars.apps.submissions.models import SubmissionSet

def test_pdf_export():
    sets = {
#        'reporter': 29,
#        'preview': 82,
        'rated': 60,
        }

    for k,v in sets.items():
        ss = SubmissionSet.objects.get(pk=v)
        outfile = "stars_report_%s.pdf" % k
        
        pdf = ss.get_pdf(False)
#        path = os.path.join(settings.PROJECT_PATH,) # the stars directory
        f = open(outfile, 'w')
        f.write(pdf)
        
if __name__ == "__main__":
    test_pdf_export()
        
    #        pdf = pisa.CreatePDF(html, file(outfile, "wb"), path)
    
    #    f = open('stars_report.html', 'w')
    #    f.write(smart_str(html))