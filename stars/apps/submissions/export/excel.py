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
    r, c = 0, 0
    sheet.col(c).width = 8000

    sheet.write_merge(r, r, c, c + 1, submission.institution.name)
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
        sheet.write(r, c, cs.category.title)
        sheet.write(r, c + 1, cs.get_STARS_score())
        r += 1


def build_category_summary_sheet(category, sheet):
    """
        Builds the summary sheet for a category
    """
    r, c = 0, 0
    sheet.col(c).width = 12000

    sheet.write_merge(r, r, c, c + 1, category.category.title)
    r += 1

    sheet.write(r, c, "Credit Number and Title")
    sheet.write(r, c + 1, "Points Earned")
    sheet.write(r, c + 2, "Available Points")
    sheet.write(r, c + 3, "Status")
    r += 2

    for sub in category.subcategorysubmission_set.all():
        sheet.write(r, c, sub.subcategory.title)
        r += 1
        for cs in sub.creditusersubmission_set.all():
            sheet.write(r, c, unicode(cs.credit))
            sheet.write(r, c + 1, cs.assessed_points)
            sheet.write(r, c + 2, cs.credit.point_value)
            sheet.write(r, c + 3, cs.get_submission_status_display())
            r += 1
        r += 1


def build_category_data_sheet(category, sheet):
    """
        Builds the data sheet for a category
    """
    r, c = 0, 0
    sheet.col(c + 1).width = 10000
    sheet.col(c + 2).width = 10000
    sheet.col(c + 3).width = 10000

    alignment = xlwt.Alignment()
    alignment.vert = xlwt.Alignment.VERT_CENTER
    style = xlwt.XFStyle()
    style.alignment = alignment

    sheet.write(r, c, "Credit")
    sheet.write(r, c + 1, "Credit Title")
    sheet.write(r, c + 2, "Reporting Field")
    sheet.write(r, c + 3, "Response")

    r += 1
    for ss in category.subcategorysubmission_set.all()[:1]:
        for cs in ss.creditusersubmission_set.all():

            responses = cs.get_submission_fields()

            sheet.write_merge(r, r + len(responses) - 1, c, c, cs.credit.identifier, style=style)
            sheet.write_merge(r, r + len(responses) - 1, c + 1, c + 1, cs.credit.title, style=style)

            for f in responses:
                sheet.write(r, c + 2, f.documentation_field.title)
                sheet.write(r, c + 3, f.get_human_value())
                r += 1


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

# from stars.apps.submissions.models import SubmissionSet
# ss = SubmissionSet.objects.get(pk=1157)
# build_report_export(ss)
