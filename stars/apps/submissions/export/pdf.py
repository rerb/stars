import cStringIO as StringIO
import os
from logging import getLogger

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from weasyprint import HTML

from stars.apps.old_cms.models import Category


logger = getLogger('stars')


def render_to_pdf(template_src, context_dict):
    """
        Creates a pdf from a template and context.
        Returns a WeasyPrint document.
    """
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    document = HTML(string=html).render()

    return document


def link_path_callback(path):
    return os.path.join(settings.MEDIA_ROOT, path)


def build_report_pdf(submission_set, template=None):
    """
        Builds a PDF export of a specific submission.
    """
    context = {'ss': submission_set,
               'preview': False,
               'media_root': settings.MEDIA_ROOT,
               'project_path': settings.PROJECT_PATH,
               'rating': submission_set.get_STARS_rating(),
               'institution': submission_set.institution,
               'host': "stars.aashe.org",
               'about_text': Category.objects.get(slug='about').content,
               'pdf': True}

    if submission_set.status != 'r':
        context['preview'] = True

    if not template:
        template = 'institutions/pdf/report.html'

    return render_to_pdf(template, context)


def build_certificate_pdf(submission_set):
    """
        Builds a PDF certificate for Institution Presidents.
    """
    context = {'ss': submission_set,
               'project_path': settings.PROJECT_PATH}
    return render_to_pdf('institutions/pdf/certificate.html', context)


def generate_outline_str(bookmarks, indent=0):
    """
    From WeasyPrint website.  Helper for generating table of contents.
    http://weasyprint.readthedocs.io/en/stable/tutorial.html

    USAGE:

    ```
    from weasyprint import HTML
    document = HTML("<HTML>...")
    table_of_contents_string = generate_outline_str(
        document.make_bookmark_tree())
    ```
    """
    outline_str = ""
    for i, (label, (page, _, _), children) in enumerate(bookmarks, 1):
        outline_str += ('%s%d. %s (page %d)' % (
            ' ' * indent, i, label.lstrip('0123456789. '), page))
        outline_str += generate_outline_str(children, indent + 2)
    return outline_str
