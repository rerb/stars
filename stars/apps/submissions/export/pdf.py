import cStringIO as StringIO
import os
from logging import getLogger

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
import ho.pisa as pisa

from stars.apps.old_cms.models import Category


logger = getLogger('stars')


def render_to_pdf(template_src, context_dict):
    """
        Creates a pdf from a template and context
        Returns a StringIO.StringIO object
    """
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
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


def build_report_pdf(submissionset, template=None):
    """Build a PDF export of a specific submission.

    If the institution has a valid full access subscription,
    scores are included.

    We build reports for three types of submissionsets.  1. Current
    submissions, which produce Preview reports, 2. Rated submissions,
    and 3. submissionsets that represent snapshots, cut to share data.

    A submissionset is sorted into one of these three types like this:

        Is submissionset status "f"?  If so, it's a snapshot.

        Is submissionset status "r"?  Then it's #2, a rated submission.

        Else, that's a current submission (Preview).

    """
    if submissionset.status == 'f':
        report_type = "snapshot"
    elif submissionset.status == 'r':
        report_type = "rated"
    else:
        report_type = "preview"

    context = {"ss": submissionset,
               "show_scores": submissionset.institution.is_participant,
               "report_type": report_type,
               "preview": report_type == "preview",
               "media_root": settings.MEDIA_ROOT,
               "project_path": settings.PROJECT_PATH,
               "rating": submissionset.get_STARS_rating(),
               "institution": submissionset.institution,
               "host": "stars.aashe.org",
               "about_text": Category.objects.get(slug="about").content,
               "pdf": True}

    if not template:
        template = "institutions/pdf/report.html"

    return render_to_pdf(template, context)


def build_certificate_pdf(ss):
    """
        Build a PDF certificate for Institution Presidents
    """
    context = {"ss": ss,
               "project_path": settings.PROJECT_PATH}

    return render_to_pdf("institutions/pdf/certificate.html", context)
