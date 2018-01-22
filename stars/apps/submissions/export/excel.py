import xlwt
from django.core.files.temp import NamedTemporaryFile

from stars.apps.submissions.models import NOT_APPLICABLE


def build_report_export(submission):
    """
        Builds the excel workbook for a specific submission
    """
    wb = xlwt.Workbook(encoding="UTF-8")

    # Summary
    summary_sheet = wb.add_sheet('Summary')
    get_summary_sheet(submission, summary_sheet)

    # Categories
    for category in submission.categorysubmission_set.all():

        sheet = wb.add_sheet("%s Summary" % category.category.abbreviation)
        build_category_detail_sheet(category, sheet)

        sheet = wb.add_sheet("%s Data" % category.category.abbreviation)
        build_credit_detail_sheet(
            category, sheet,
            use_metric=submission.institution.prefers_metric_system)

    tempfile = NamedTemporaryFile(suffix='.xls', delete=False)

    wb.save(tempfile.name)
    return tempfile.name


def get_summary_sheet(submissionset, sheet):
    """
        Builds the first sheet of an exported report that
        has the summary of the submissionset
    """
    boldFont = xlwt.Font()
    boldFont.bold = True
    boldStyle = xlwt.XFStyle()
    boldStyle.font = boldFont

    r, c = 0, 0
    min_width = get_width(len(submissionset.institution.name))

    sheet.write_merge(r, r, c, c + 1,
                      submissionset.institution.name, boldStyle)
    r += 1

    sheet.write_merge(r, r, c, c + 1, 'STARS Report Summary')
    r += 1

    export_type = get_export_type(submissionset)

    if export_type == "preview":
        sheet.write(r, c, "Exported:")
    elif export_type == "snapshot":
        sheet.write(r, c, "Snapshot:")
    else:
        sheet.write(r, c, "Submitted:")
    sheet.write(r, c + 1, "%s" % submissionset.date_submitted)
    r += 1

    sheet.write(r, c, "Rating:")
    sheet.write(r, c + 1, "%s" % submissionset.rating)
    r += 2

    sheet.write(r, c, "Category")
    sheet.write(r, c + 1, "Points Earned")
    sheet.write(r, c + 2, "Available Points")
    r += 1

    for cs in submissionset.categorysubmission_set.all():
        if min_width < get_width(len(cs.category.title)):
            min_width = get_width(len(cs.category.title))
        sheet.write(r, c, cs.category.title)
        if submissionset.creditset.version in ("1.0", "1.1", "1.2"):
            sheet.write(r, c + 1, str(cs.get_STARS_score()))
        else:
            sheet.write(r, c + 1, str(cs.get_score_ratio()[0]))
            sheet.write(r, c + 2, str(cs.get_score_ratio()[1]))

        r += 1

    r += 1
    sheet.write(r, c, "Total Score")
    sheet.write(r, c + 1, str(submissionset.get_STARS_score()))

    sheet.col(c).width = min_width


def build_category_detail_sheet(category, sheet):
    """
        Builds the detail sheet for a category.
    """
    boldFont = xlwt.Font()
    boldFont.bold = True
    boldStyle = xlwt.XFStyle()
    boldStyle.font = boldFont

    r, c = 0, 0
    min_width = 12000

    sheet.write_merge(r, r, c, c + 1, category.category.title, boldStyle)
    r += 1

    sheet.write(r, c, "Credit Number and Title")
    sheet.write(r, c + 1, "Points Earned")
    sheet.write(r, c + 2, "Available Points")
    sheet.write(r, c + 3, "Status")
    sheet.write(r, c + 4, "Last Updated")
    sheet.write(r, c + 5, "Responsible Party")
    sheet.write(r, c + 6, "Data Source(s) and Notes")

    r += 1

    for sub in category.subcategorysubmission_set.all():
        if min_width < get_width(len(sub.subcategory.title)):
            min_width = get_width(len(sub.subcategory.title))

        sheet.write(r, c, sub.subcategory.title, boldStyle)
        sheet.write(r, c + 1, sub.description)
        r += 1
        for cs in sub.creditusersubmission_set.all():
            # Skip opt-in credits with status of NA:
            if cs.credit.is_opt_in and cs.submission_status == NOT_APPLICABLE:
                continue
            if min_width < get_width(len(unicode(cs.credit))):
                min_width = get_width(len(unicode(cs.credit)))
            sheet.write(r, c, unicode(cs.credit))
            sheet.write(r, c + 1, cs.assessed_points)
            sheet.write(r, c + 2, cs.credit.point_value)
            sheet.write(r, c + 3, cs.get_submission_status_display())
            sheet.write(r, c + 4, cs.last_updated)

            full_name = ''
            if cs.responsible_party:  # might be None
                if cs.responsible_party.first_name:
                    full_name += cs.responsible_party.first_name
                    if cs.responsible_party.last_name:
                        if full_name:
                            full_name += ' '
                        full_name += cs.responsible_party.last_name

            sheet.write(r, c + 5, full_name)

            sheet.write(r, c + 6, cs.submission_notes)
            r += 1
        r += 1

    sheet.col(c).width = min_width
    for c in range(1, 5):
        sheet.col(c).width = 5000


def build_credit_detail_sheet(category, sheet, use_metric):
    """
        Builds the data sheet for a category
    """

    col_widths = [3000, 5000, 10000, 15000]
    max_widths = [8000, 20000, 20000, 20000]

    def update_width(column, content):
        if col_widths[column] < get_width(len(content)):
            col_widths[column] = get_width(len(content))
        if col_widths[column] > max_widths[column]:
            col_widths[column] = max_widths[column]

    borders = xlwt.Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1

    borderedStyle = xlwt.XFStyle()
    borderedStyle.borders = borders

    boldFont = xlwt.Font()
    boldFont.bold = True

    boldBorderedStyle = xlwt.XFStyle()
    boldBorderedStyle.borders = borders
    boldBorderedStyle.font = boldFont

    alignment = xlwt.Alignment()
    alignment.vert = xlwt.Alignment.VERT_CENTER
    centeredBorderedStyle = xlwt.XFStyle()
    centeredBorderedStyle.borders = borders
    centeredBorderedStyle.alignment = alignment

    r, c = 0, 0

    sheet.write(r, c, "Credit", boldBorderedStyle)
    update_width(c, "Credit")
    sheet.write(r, c + 1, "Credit Title", boldBorderedStyle)
    sheet.write(r, c + 2, "Reporting Field", boldBorderedStyle)
    sheet.write(r, c + 3, "Response", boldBorderedStyle)

    r += 1
    for subcategory_submission in category.subcategorysubmission_set.all():
        for credit_submission in (
             subcategory_submission.creditusersubmission_set.all()):

            # Skip opt-in credits with status of NA:
            if (credit_submission.credit.is_opt_in and
                credit_submission.submission_status == NOT_APPLICABLE):  # noqa

                continue

            submission_fields = credit_submission.get_submission_fields()

            sheet.write_merge(r, r + len(submission_fields) - 1, c, c,
                              credit_submission.credit.identifier,
                              style=centeredBorderedStyle)
            update_width(c, credit_submission.credit.identifier)
            sheet.write_merge(r, r + len(submission_fields) - 1, c + 1, c + 1,
                              credit_submission.credit.title,
                              style=centeredBorderedStyle)
            update_width(c + 1, credit_submission.credit.title)

            for submission_field in submission_fields:
                sheet.write(r, c + 2,
                            submission_field.documentation_field.title,
                            borderedStyle)
                update_width(c + 2, submission_field.documentation_field.title)
                sheet.write(
                    r, c + 3,
                    submission_field.get_human_value(get_metric=use_metric),
                    borderedStyle)
                r += 1

    for c, w in enumerate(col_widths):
        sheet.col(c).width = w


def get_width(num_characters):
    return int((1 + num_characters) * 256)


def get_export_type(submissionset):

    if submissionset.status == 'f':
        report_type = "snapshot"
    elif submissionset.status == 'r':
        report_type = "rated"
    else:
        report_type = "preview"

    return report_type
