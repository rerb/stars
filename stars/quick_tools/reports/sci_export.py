"""
    Hint:
        $ PYTHONIOENCODING=UTF-8 ./manage.py shell
        In [1]: %run stars/quick_tools/reports/sci_export.py
"""

"""

- Report format
    - Excel, CSV or Google sheet file(s)
    - Ideal to have a single file with multiple tabs, but it's fine if it
ends up being a folder with lots of files.
    - Ideal to include version 1, 2.0, and 2.1 reports in the same file,
but it's fine if they have to be presented in separate files.
- Report structure:
    - Score data for each STARS subcategory (Curriculum, Research, Campus
Engagement, Public Engagement, ...), plus a file or tab that has all
institutions by OVERALL Score.
    - See the report I created last year (attached) to get a sense of the
ideal structure.
    - Report must include data in the following columns:
    - Institution Name
    - Submit Date
    - STARS version
    - Points earned in X
    - Points available for X - Make sure there is a difference between
Not Applicable and Not Pursuing since in subcategories like Research,
institutions select Not Applicable across all credits
    - Not Applicable means points available is zero, or simply state
Not Applicable in this field)
- Not Pursuing means points available is whatever their
subcategory score was based on - greater than zero
- Nice to include but not necessary if it's extra work (I can add
this myself pretty easily using Excel data merge)
- Institution Type based on Salesforce Data
- Country
- Calculated Percentage based on points earned/available
- Nth report and total reports submitted (see attached file)
"""

from django.db.models import Q

from stars.apps.submissions.models import (
    SubmissionSet, SubcategorySubmission, SUBMISSION_STATUSES)
from stars.apps.credits.models import CreditSet

import datetime

"""
- All published version 1, 2.0 and 2.1 reports that are valid (i.e. not
Expired) at 11:59pm EST on June 30, 2016 (anything with a submit date of
July 1, 2013 and later)
- Need to include reports that have been FINALIZED BUT NOT PUBLISHED,
i.e., those that submitted in May/June 2016 that have not yet addressed the
review results.
- If an institution submitted more than one report, make sure they are
all included.
"""

DEADLINE = datetime.date(year=2016, month=6, day=30)

cs_id_list = [2, 4, 5, 6, 7]  # 1.0 - 2.1
# response = raw_input("Enter a Creditset ID: ")
# cs_id_list = [response]

for cs_id in cs_id_list:
    cs = CreditSet.objects.get(pk=cs_id)

    ss_qs = SubmissionSet.objects.filter(creditset=cs)
    ss_qs = ss_qs.filter(
        status__in=[
            SUBMISSION_STATUSES["RATED"],
            SUBMISSION_STATUSES["REVIEW"]])

    ss_qs = ss_qs.filter(expired=False).filter(date_submitted__lte=DEADLINE)

    # Subcategory Scores Sheet
    filename = "%s_subcategory_scores.csv" % cs.version
    outfile = open(filename, 'w+')
    print "writing to: %s" % filename

    subcat_headers = [
        "Institution Name",
        "Status",
        "Submit Date",
        "STARS version",
        "Overall Score",
        "Rating",
        "Institution Type",
        "Country",
        "Nth Report (includes expired)",
        "# Reports Submitted (includes expired)",
    ]

    # Add the subcategories
    subcategories = []  # stored for later reference
    for cat in cs.category_set.all():
        for sub in cat.subcategory_set.all():
            subcategories.append(sub)
            subcat_headers.append("%s points claimed" % sub.title)
            subcat_headers.append("%s points available" % sub.title)

    print >>outfile, "\t".join(subcat_headers)

    for ss in ss_qs:
        row = []
        row.append(ss.institution.name)
        row.append(ss.status)
        row.append(unicode(ss.date_submitted))
        row.append(ss.creditset.version)
        row.append("%f.2" % ss.score)
        row.append(ss.rating.name)
        row.append(ss.institution.org_type)
        row.append(ss.institution.country)

        # calculated total reports submitted
        all_reports = ss.institution.submissionset_set.filter(
            status__in=[
                SUBMISSION_STATUSES["RATED"],
                SUBMISSION_STATUSES["REVIEW"]]
            ).order_by('date_submitted').values_list('id', 'date_submitted')
        # print all_reports
        # print ss.id
        index = [x[0] for x in all_reports].index(ss.id)

        row.append(unicode(index + 1))
        row.append(unicode(len(all_reports)))

        for sub in subcategories:
            subcatsub = SubcategorySubmission.objects.filter(
                subcategory=sub).get(category_submission__submissionset=ss)
            row.append(unicode(subcatsub.get_claimed_points()))
            row.append(unicode(subcatsub.get_adjusted_available_points()))

        try:
            print >>outfile, u"\t".join(row)
        except:
            print "***Failed to encode"
            print u"\t".join(row)
    outfile.close()
