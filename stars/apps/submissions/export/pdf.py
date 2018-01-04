import collections
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
    """
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    document = HTML(string=html).render()

    return document


def insert_table_of_contents(document, submissionset):
    """
    Inserts table of contents into WeasyPrint.Document "document".
    """
    toc = HTML(
        string=generate_table_of_contents_string(document,
                                                 submissionset)).render()

    for toc_page in reversed(toc.pages):
        document.pages.insert(0, toc_page)

    return document


Bookmark = collections.namedtuple("Bookmark", "kind label page")


def generate_table_of_contents_string(document, submissionset):

    cooked_bookmarks = cook_bookmarks(document.make_bookmark_tree())
    bookmarks = []

    # Get Category bookmarks:
    for category in submissionset.creditset.category_set.all():
        for bookmark in cooked_bookmarks:
            if bookmark[0] == category.title.strip():
                bookmarks.append(Bookmark(kind="category",
                                          label=bookmark[0],
                                          page=bookmark[1]))
                cooked_bookmarks.remove(bookmark)
                break
        else:
            logger.error("No bookmark for category '{}'".format(
                category.title))

        # Get Subcategory of Category bookmarks:
        for subcategory in category.subcategory_set.all():
            for bookmark in cooked_bookmarks:
                if bookmark[0] == subcategory.title.strip():
                    bookmarks.append(Bookmark(kind="subcategory",
                                              label=bookmark[0],
                                              page=bookmark[1]))
                    cooked_bookmarks.remove(bookmark)
                    break
            else:
                logger.error("No bookmark for subcategory '{}'".format(
                    subcategory.title))

            # Get Credit of Subcategory bookmarks:
            for credit in subcategory.credit_set.all():
                for bookmark in cooked_bookmarks:
                    if bookmark[0] == credit.title.strip():
                        bookmarks.append(Bookmark(kind="credit",
                                                  label=bookmark[0],
                                                  page=bookmark[1]))
                        cooked_bookmarks.remove(bookmark)
                        break
                # No error if there's no bookmark for a credit -- assume
                # those are optional (opt-in) credits that haven't been
                # opted-into.

    toc_string = (TOC_HEAD +
                  "<table cellpadding=\"0\" cellspacing=\"0\""
                  "style=\"border-spacing: 0px\">")

    for bookmark in bookmarks:
        if bookmark.kind == "category":
            toc_string += format_category_bookmark(bookmark)
        elif bookmark.kind == "subcategory":
            toc_string += format_subcategory_bookmark(bookmark)
        elif bookmark.kind == "credit":
            credit_submission = get_credit_submission(
                title=bookmark.label,
                submissionset=submissionset)
            toc_string += format_credit_bookmark(
                bookmark=bookmark,
                credit_submission=credit_submission)
        else:
            raise Exception("what kind of bookmark is this? " + str(bookmark))

    return toc_string + "</table></body>"


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
    return ("<tr style=\"font-size: 12pt;\">"
            "<td colspan=\"2\">{label}</td>"
            "<td></td>"
            "<td></td>"
            "<td></td>"
            "<td></td>"
            "<td>{page}</td>"
            "</tr>".format(
                label=bookmark.label,
                page=bookmark.page))


def format_subcategory_bookmark(bookmark):
    # Don't print the subcategory Institutional Characteristics since
    # the parent Category is called Institutional Characteristics too.
    if bookmark.label.lower() != "institutional characteristics":
        return ("<tr style=\"font-size: 11pt;\">"
                "<td></td>"
                "<td colspan=\"2\">{label}</td>"
                "<td></td>"
                "<td></td>"
                "<td></td>"
                "<td>{page}</td>"
                "</tr>".format(
                    label=bookmark.label,
                    page=bookmark.page))


def get_credit_submission(title, submissionset):
    # Import CreditUserSubmission way down here to side-step
    # a circular dependency.
    from stars.apps.submissions.models import CreditUserSubmission

    ss = submissionset
    return CreditUserSubmission.objects.get(
        subcategory_submission__category_submission__submissionset=ss,
        credit__title=title)


def format_credit_bookmark(bookmark, credit_submission):
    # Import credit status constants down here to avoid
    # a circular dependency.
    from stars.apps.submissions.models import (COMPLETE,
                                               IN_PROGRESS,
                                               NOT_PURSUING,
                                               NOT_APPLICABLE,
                                               NOT_STARTED)

    credit_submission_status_words = {COMPLETE: "Complete",
                                      IN_PROGRESS: "In progress",
                                      NOT_PURSUING: "Not pursuing",
                                      NOT_APPLICABLE: "Not applicable",
                                      NOT_STARTED: "Not started"}

    return ("<tr style=\"font-size: 10pt;\">"
            "<td></td>"
            "<td></td>"
            "<td colspan\"2\">{label}</td>"
            "<td>{status}</td>"
            "<td>{points:g}/{available:g}</td>"
            "<td></td>"
            "<td>{page}</td>"
            "</tr>".format(
                label=bookmark.label,
                page=bookmark.page,
                status=credit_submission_status_words[
                    credit_submission.submission_status],
                points=credit_submission.assessed_points,
                available=credit_submission.get_adjusted_available_points()))


# don't think link_path_callback is used by Weasyprint
# def link_path_callback(path):
#     return os.path.join(settings.MEDIA_ROOT, path)


def build_report_pdf(submissionset, template=None):
    """
        Builds a PDF export of a specific submission.
    """
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
        context['preview'] = True

    if not template:
        template = 'institutions/pdf/report.html'

    report = render_to_pdf(template, context)

    report_with_toc = insert_table_of_contents(report, submissionset)

    return report_with_toc


def build_certificate_pdf(submissionset):
    """
        Builds a PDF certificate for Institution Presidents.
    """
    context = {'ss': submissionset,
               'project_path': settings.PROJECT_PATH}
    return render_to_pdf('institutions/pdf/certificate.html', context)


TOC_HEAD = """
<html>

  <head>

  </head>

  <body style="font-family: Arial, sans-serif; font-size: 12pt;">

"""
