import cStringIO as StringIO
import ho.pisa as pisa
from logging import getLogger
from cgi import escape
import sys, os
from datetime import datetime

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.utils.encoding import smart_str, smart_unicode

from stars.apps.institutions.models import * # required for execfile management func
from stars.apps.cms.models import Category

logger = getLogger('stars')

def render_to_pdf(template_src, context_dict):
    """
        Creates a pdf from a temlate and context
        Returns a StringIO.StringIO object
    """

    template = get_template(template_src)
    context = Context(context_dict)
#    print >> sys.stdout, "Building PDF"
#    print >> sys.stdout, "%s: Generating HTML" % datetime.now()
    html = template.render(context)
#    print >> sys.stdout, "%s: Finished HTML" % datetime.now()
    result = StringIO.StringIO()
#    print >> sys.stdout, "RESULT"
#    print >> sys.stderr, html

    # print >> sys.stdout, "%s: Generating PDF" % datetime.now()
    pdf = pisa.pisaDocument(html, result)
    # print >> sys.stdout, "%s: Finished PDF" % datetime.now()

    if not pdf.err:
        return result
    else:
        msg = "PDF Generation Failed %s" % html
        print >> sys.stderr, msg
        logger.error(msg)
        return None

def link_path_callback(path):
    return os.path.join(settings.MEDIA_ROOT, path)

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

def build_certificate_pdf(ss):
    """
        Build a PDF certificate for Institution Presidents
    """

    context = {
                'ss': ss,
                'project_path': settings.PROJECT_PATH,
                }
    return render_to_pdf('institutions/pdf/certificate.html', context)
