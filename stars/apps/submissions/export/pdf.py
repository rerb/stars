import collections
import cStringIO as StringIO
import os
from logging import getLogger

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
<<<<<<< Updated upstream
import ho.pisa as pisa
=======
from weasyprint import CSS, HTML
>>>>>>> Stashed changes

from stars.apps.old_cms.models import Category


logger = getLogger('stars')


def render_to_pdf(template_src, context_dict):
    """
<<<<<<< Updated upstream
        Creates a pdf from a temlate and context
        Returns a StringIO.StringIO object
=======
    Creates a pdf from a template and context.

    Inserts a table of contents into a WeasyPrint
    document and returns it.
>>>>>>> Stashed changes
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


def insert_table_of_contents(document, submissionset):
    """
    Inserts table of contents into WeasyPrint.Document "document".
    """
    toc_doc = HTML(string=generate_table_of_contents_string(
        document, submissionset)).render()
    document.pages.insert(0, toc_doc.pages[0])
    return document


Bookmark = collections.namedtuple("Bookmark", "kind label page")


def generate_table_of_contents_string(document, submissionset):
    cooked_bookmarks = cook_bookmarks(document.make_bookmark_tree())
    bookmarks = []

    # Get Category bookmarks:
    for category in submissionset.creditset.category_set.all():
        for bookmark in cooked_bookmarks:
            if bookmark[0] == category.title:
                bookmarks.append(Bookmark(kind="category",
                                          label=bookmark[0],
                                          page=bookmark[1]))
                del(bookmark)
                break
        else:
            logger.error("No bookmark for category '{}'".format(
                category.title))

        # Get Subcategory of Category bookmarks:
        for subcategory in category.subcategory_set.all():
            for bookmark in cooked_bookmarks:
                if bookmark[0] == subcategory.title:
                    bookmarks.append(Bookmark(kind="subcategory",
                                              label=bookmark[0],
                                              page=bookmark[1]))
                    del(bookmark)
                    break
            else:
                logger.error("No bookmark for subcategory '{}'".format(
                    subcategory.title))

            # Get Credit of Subcategory bookmarks:
            for credit in subcategory.credit_set.all():
                for bookmark in cooked_bookmarks:
                    if bookmark[0] == credit.title:
                        bookmarks.append(Bookmark(kind="credit",
                                                  label=bookmark[0],
                                                  page=bookmark[1]))
                        del(bookmark)
                        break
                else:
                    logger.error("No bookmark for credit '{}'".format(
                        credit.title))

    toc_string = "<table class=\"toc\">"

    for category in submissionset.creditset.category_set.all():
        for bookmark in bookmarks:
            if (bookmark.kind == "category" and
                category.title == bookmark.label):

                toc_string += format_category_bookmark(bookmark)
                break
        else:
            logger.error("No bookmark for category '{}'".format(
                category.title))
        for subcategory in category.subcategory_set.all():
            for bookmark in bookmarks:
                if (bookmark.kind == "subcategory" and
                    subcategory.title == bookmark.label):

                    toc_string += format_subcategory_bookmark(bookmark)
                    break
            else:
                logger.error("No bookmark for subcategory '{}'".format(
                    subcategory.title))
            for credit in subcategory.credit_set.all():
                for bookmark in bookmarks:
                    if (bookmark.kind == "credit" and
                        credit.title == bookmark.label):

                        toc_string += format_credit_bookmark(bookmark)
                        break
                else:
                    logger.error("No bookmark for credit '{}'".format(
                        credit.title))

    return toc_string + "<table>"


def cook_bookmarks(bookmarks, cooked=None):
    """
    Turns a WeasyPrint document's bookmarks into a list of
    (label, page) tuples.
    """
    if cooked is None:
        cooked = []
    for i, (label, (page, _, _,), children) in enumerate(bookmarks, 1):
        cooked.append((label, page))
        cook_bookmarks(children, cooked)
    return cooked


def format_category_bookmark(bookmark):
    return "<tr><td>CATEGORY {label}</td><td>{page}</td></tr>".format(
        label=bookmark.label,
        page=bookmark.page)


def format_subcategory_bookmark(bookmark):
    return ("<tr><td class=\"toc-subcategory\">"
            "SUBCATEGORY {label}</td><td>{page}</td></tr>".format(
                label=bookmark.label,
                page=bookmark.page))


def format_credit_bookmark(bookmark):
    return ("<tr><td class=\"toc-credit\">"
            "CREDIT {label}</td><td>{page}</td></tr>".format(
                label=bookmark.label,
                page=bookmark.page))


def link_path_callback(path):
    return os.path.join(settings.MEDIA_ROOT, path)


def build_report_pdf(submissionset, template=None):
    """
        Build a PDF export of a specific submission
        store it in outfile, if submitted
        if save if True, the file will be saved
    """
<<<<<<< Updated upstream
    context = {
                'ss': submission_set,
                'preview': False,
                'media_root': settings.MEDIA_ROOT,
                'project_path': settings.PROJECT_PATH,
                'rating': submission_set.get_STARS_rating(),
                'institution': submission_set.institution,
                'host': "stars.aashe.org",
                'about_text': Category.objects.get(slug='about').content,
                'pdf': True
            }
    if submission_set.status != 'r':
=======
    context = {'ss': submissionset,
               'preview': False,
               'media_root': settings.MEDIA_ROOT,
               'project_path': settings.PROJECT_PATH,
               'rating': submissionset.get_STARS_rating(),
               'institution': submissionset.institution,
               'host': "stars.aashe.org",
               'about_text': Category.objects.get(slug='about').content,
               'pdf': True}

    if submissionset.status != 'r':
>>>>>>> Stashed changes
        context['preview'] = True

    if not template:
        template = 'institutions/pdf/report.html'
<<<<<<< Updated upstream
    return render_to_pdf(template, context)
=======

    report = render_to_pdf(template, context)

    report_with_toc = insert_table_of_contents(report, submissionset)
>>>>>>> Stashed changes

    return report_with_toc

<<<<<<< Updated upstream
def build_certificate_pdf(ss):
=======
def build_certificate_pdf(submissionset):
>>>>>>> Stashed changes
    """
        Build a PDF certificate for Institution Presidents
    """
<<<<<<< Updated upstream
    context = {
                'ss': ss,
                'project_path': settings.PROJECT_PATH,
                }
=======
    context = {'ss': submissionset,
               'project_path': settings.PROJECT_PATH}
>>>>>>> Stashed changes
    return render_to_pdf('institutions/pdf/certificate.html', context)
