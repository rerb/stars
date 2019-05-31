import cStringIO as StringIO
import os
from logging import getLogger

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from xhtml2pdf import pisa as pisa

from stars.apps.old_cms.models import Category


logger = getLogger('stars')


def render_to_pdf(template_src, context_dict):
    """
        Creates a pdf from a temlate and context
        Returns a StringIO.StringIO object
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(html, result)

    if not pdf.err:
        return result
    else:
        msg = "PDF Generation Failed %s" % html
        logger.error(msg)
        return None


def link_path_callback(path):
    return os.path.join(settings.MEDIA_ROOT, path)


def build_report_pdf(submission_set, template=None):
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
        'host': "reports.aashe.org",
                'about_text': Category.objects.get(slug='about').content,
                'pdf': True
    }
    if submission_set.status != 'r':
        context['preview'] = True

    if not template:
        template = 'institutions/pdf/report.html'
    return render_to_pdf(template, context)


def build_certificate_pdf(ss):
    """
        Build a PDF certificate for Institution Presidents
    """
    context = {
        'ss': ss,
        'project_path': settings.PROJECT_PATH,
    }
    return render_to_pdf('institutions/pdf/certificate.html', context)
