from django.utils.encoding import smart_str
from django.core.files.temp import NamedTemporaryFile

from stars.apps.submissions.models import (SubmissionSet,
                                           CreditUserSubmission,
                                           DocumentationFieldSubmission
                                           )

import string, csv


def export_credit_csv(credit, ss_qs=None):
    """
        Returns a NamedTemporaryFile with data from each submisisonset
        in ss_qs for the specified credit.
    """
    tempfile = NamedTemporaryFile(suffix='.csv', delete=False)
    csvWriter = csv.writer(tempfile)

    # Get the list of submissions for columns
    if not ss_qs:
        ss_qs = SubmissionSet.objects.filter(status='r').order_by("institution__name")
    ss_list = []
    cus_list = []
    for ss in ss_qs:
        ss_list.append(ss)
        cus = CreditUserSubmission.objects.get(credit=credit.get_for_creditset(ss.creditset), subcategory_submission__category_submission__submissionset=ss)
        cus_list.append(cus)

    # Get the list of fields in the credit for rows
    df_list = []
    for df in credit.documentationfield_set.all():
        df_list.append(df)

    # Create Columns

    columns = [
                "Institution",
                "Date Submitted",
                "Last Updated",
                "Liason Email",
#                "City",
#                "State",
#                "Country",
#                "Org type",
#                "FTE-Enrollment",
                "Version",
                "Status",
               ]

    for df in df_list:
        columns.append(df)

    columns.append('Public Notes')

    csvWriter.writerow(columns)

    # Create Rows
    for cus in cus_list:

        institution = cus.get_institution()
        ss = cus.subcategory_submission.category_submission.submissionset

        row = [
                institution.name,
                ss.date_submitted,
                cus.last_updated,
                institution.contact_email,
#                profile.city,
#                profile.state,
#                institution.country,
#                institution.org_type,
#                institution.fte,
                ss.creditset.version
                ]

        # Status and Score
        if cus.submission_status == "na":
            row.append("Not Applicable")
        elif cus.submission_status == 'np' or cus.submission_status == 'ns':
            row.append("Not Pursuing")
        else:
            row.append("Pursuing")

        for df in df_list:

            if (cus.submission_status == "na" or
                cus.submission_status == 'np' or
                cus.submission_status == 'ns'):
                row.append("--")
            else:
                field_class = DocumentationFieldSubmission.get_field_class(df)
                try:
                    _df = df.get_for_creditset(ss.creditset)
                    dfs = field_class.objects.get(credit_submission=cus,
                                                  documentation_field=_df)
                except:
                    row.append('**')
                else:
                    if df.type == 'upload':
                        if dfs.value:
                            row.append("http://stars.aashe.org%s" %
                                       dfs.value.url)
                        else:
                            row.append("")
                    else:
                        # long text has to be truncated for excel
                        if dfs.documentation_field.type == 'long_text':
                            if dfs.value:
                                str_val = dfs.value.replace("\r\n", "\n")
                                if len(str_val) > 32000:
                                    str_val = ("%s [TRUNCATED]" %
                                               str_val[:32000])
                            else:
                                str_val = ""
                            row.append(smart_str(str_val))

                        else:
                            row.append(smart_str(dfs.value))
        row.append(smart_str(cus.submission_notes))
        csvWriter.writerow(row)

    tempfile.close()
    print "Closing tempfile: %s" % tempfile.name
    return tempfile.name
    