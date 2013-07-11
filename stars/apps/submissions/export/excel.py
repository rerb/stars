import xlwt

from django.template.defaultfilters import slugify
from django.core.files.temp import NamedTemporaryFile

from django.conf import settings


def get_width(num_characters):
    return int((1 + num_characters) * 256)


def get_summary_sheet(submission, sheet):
    """
        Builds the first sheet of an exported report that
        has the summary of the submission
    """
    boldFont = xlwt.Font()
    boldFont.bold = True
    boldStyle = xlwt.XFStyle()
    boldStyle.font = boldFont

    r, c = 0, 0
    min_width = get_width(len(submission.institution.name))

    sheet.write_merge(r, r, c, c + 1, submission.institution.name, boldStyle)
    r += 1

    sheet.write_merge(r, r, c, c + 1, 'STARS Report Summary')
    r += 1

    sheet.write(r, c, "Submitted:")
    sheet.write(r, c + 1, "%s" % submission.date_submitted)
    r += 1

    sheet.write(r, c, "Rating:")
    sheet.write(r, c + 1, "%s" % submission.rating)
    r += 2

    sheet.write(r, c, "Category")
    sheet.write(r, c + 1, "Score")
    r += 1

    for cs in submission.categorysubmission_set.all():
        if min_width < get_width(len(cs.category.title)):
            min_width = get_width(len(cs.category.title))
        sheet.write(r, c, cs.category.title)
        sheet.write(r, c + 1, cs.get_STARS_score())
        r += 1

    sheet.col(c).width = min_width


def build_category_summary_sheet(category, sheet):
    """
        Builds the summary sheet for a category
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
    r += 2

    for sub in category.subcategorysubmission_set.all():
        if min_width < get_width(len(sub.subcategory.title)):
            min_width = get_width(len(sub.subcategory.title))

        sheet.write(r, c, sub.subcategory.title, boldStyle)
        r += 1
        for cs in sub.creditusersubmission_set.all():
            if min_width < get_width(len(unicode(cs.credit))):
                min_width = get_width(len(unicode(cs.credit)))
            sheet.write(r, c, unicode(cs.credit))
            sheet.write(r, c + 1, cs.assessed_points)
            sheet.write(r, c + 2, cs.credit.point_value)
            sheet.write(r, c + 3, cs.get_submission_status_display())
            r += 1
        r += 1

    sheet.col(c).width = min_width
    for c in range(1, 5):
        sheet.col(c).width = 5000


def build_category_data_sheet(category, sheet):
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
    for ss in category.subcategorysubmission_set.all()[:1]:
        for cs in ss.creditusersubmission_set.all():

            responses = cs.get_submission_fields()

            sheet.write_merge(r, r + len(responses) - 1, c, c, cs.credit.identifier, style=centeredBorderedStyle)
            update_width(c, cs.credit.identifier)
            sheet.write_merge(r, r + len(responses) - 1, c + 1, c + 1, cs.credit.title, style=centeredBorderedStyle)
            update_width(c + 1, cs.credit.title)

            for f in responses:
                sheet.write(r, c + 2, f.documentation_field.title, borderedStyle)
                update_width(c + 2, f.documentation_field.title)
                sheet.write(r, c + 3, f.get_human_value(), borderedStyle)
                r += 1

    for c, w in enumerate(col_widths):
        sheet.col(c).width = w


def build_report_export(submission):
    """
        Builds the excel workbook for a specific submission
    """
    print "STARTING EXCEL EXPORT"
    wb = xlwt.Workbook()

    # Summary
    summary_sheet = wb.add_sheet('Summary')
    get_summary_sheet(submission, summary_sheet)

    # Categories
    for category in submission.categorysubmission_set.all():
        sheet = wb.add_sheet("%s Summary" % category.category.abbreviation)
        build_category_summary_sheet(category, sheet)
        sheet = wb.add_sheet("%s Data" % category.category.abbreviation)
        build_category_data_sheet(category, sheet)

#     filename = "%s.xls" % slugify("%s" % submission)
    tempfile = NamedTemporaryFile(suffix='.xls', delete=False)
#     filename = "report_export.xls"

    print tempfile.name
    wb.save(tempfile.name)
    return tempfile.name

from stars.apps.submissions.models import SubmissionSet
ss = SubmissionSet.objects.get(pk=1157)
build_report_export(ss)
