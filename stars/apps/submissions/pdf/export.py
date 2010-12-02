import cStringIO as StringIO
import ho.pisa as pisa
from cgi import escape
import sys, os
from datetime import datetime

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.utils.encoding import smart_str, smart_unicode

from stars.apps.institutions.models import * # required for execfile management func
#from stars.apps.submissions.models import SubmissionSet
from stars.apps.cms.models import Category
from stars.apps.helpers import watchdog

def render_to_pdf(template_src, context_dict):
    """
        Creates a pdf from a temlate and context
        Returns a StringIO.StringIO object
    """
    
    template = get_template(template_src)
    context = Context(context_dict)
    print >> sys.stderr, "Building PDF"
    print >> sys.stderr, "%s: Generating HTML" % datetime.now()
    html  = template.render(context)
    print >> sys.stderr, "%s: Finished HTML" % datetime.now()
    result = StringIO.StringIO()
    
    print >> sys.stderr, "%s: Generating PDF" % datetime.now()
    pdf = pisa.pisaDocument(html, result)
    print >> sys.stderr, "%s: Finished PDF" % datetime.now()
    

    if not pdf.err:
        return result
    else:
        watchdog.log("PDF Tool", "PDF Generation Failed %s" % html, watchdog.ERROR)
        return None
            
    if not pdf.err:
        return result
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

def link_path_callback(path):
    return "%spath" % settings.MEDIA_ROOT

def build_report_pdf(submission_set):
    """
        Build a PDF export of a specific submission
        store it in outfile, if submitted
        if save if True, the file will be saved
    """
    context = {
                'ss': submission_set,
                'preview': False,
                'media_root': settings.MEDIA_ROOT,
                'project_path': settings.PROJECT_PATH,
                'rating': submission_set.get_STARS_rating(),
                'institution': submission_set.institution,
                'host': "stars.aashe.org",
                'about_text': Category.objects.get(slug='about').content,
            }
    if submission_set.status != 'r':
        context['preview'] = True
    
    return render_to_pdf('institutions/pdf/report.html', context)

#def test_pdf_export():
#    
#    sets = {
##        'reporter': 29,
##        'preview': 82,
#        'rated': 60,
#        }
#    
#    #    ss = SubmissionSet.objects.get(pk=29) # reporter
#    #    ss = SubmissionSet.objects.get(pk=82) # preview
#    #    ss = SubmissionSet.objects.get(pk=60) # rated
#
#    for k,v in sets.items():
#        ss = SubmissionSet.objects.get(pk=v)
#        outfile = "stars_report_%s.pdf" % k
#        
#        pdf_result = build_report_pdf(ss)
#        path = os.path.join(settings.PROJECT_PATH,) # the stars directory
#        f = open(outfile, 'w')
#        f.write(pdf_result.getvalue())
##        pdf = pisa.CreatePDF(html, file(outfile, "wb"), path)
#
##    f = open('stars_report.html', 'w')
##    f.write(smart_str(html))
#
#if __name__ == "__main__":
#    test_pdf_export()
