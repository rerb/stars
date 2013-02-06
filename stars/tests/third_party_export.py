#!/usr/bin/env python

"""
    Tool to export all content for a specific credit
"""

from stars.apps.institutions.models import *
from stars.apps.submissions.models import *
from stars.apps.credits.models import Credit

from django.utils.encoding import smart_unicode, smart_str

import csv, string

def export_credit_content(credit, ss_qs=None):
    
    print ss_qs

    filename = 'export/%s.csv' % string.replace("%s" % credit, "/", "-")
    filename = string.replace(filename, ":", "")
    filename = string.replace(filename, " ", "_")
    print filename
    csvWriter = csv.writer(open(filename, 'wb'))
    
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
        
        institution = cus.subcategory_submission.category_submission.submissionset.institution
        profile = institution.profile
#        print institution
        
        row = [
                institution.name,
                institution.contact_email,
#                profile.city,
#                profile.state,
#                institution.country,
#                institution.org_type,
#                institution.fte,
                cus.subcategory_submission.category_submission.submissionset.creditset.version
                ]
        
        # Status and Score
        if cus.submission_status == "na":
            row.append("Not Applicable")
        elif cus.submission_status == 'np' or cus.submission_status == 'ns':
            row.append("Not Pursuing")
        else:
            row.append("Pursuing")
        
        for df in df_list:
            
            if cus.submission_status == "na" or cus.submission_status == 'np' or cus.submission_status == 'ns':
                row.append("--")
            else:
                field_class = DocumentationFieldSubmission.get_field_class(df)
                try:
                    dfs = field_class.objects.get(credit_submission=cus, documentation_field=df.get_for_creditset(cus.subcategory_submission.category_submission.submissionset.creditset))
                except:
                    row.append('**')
                else:
                    if df.type == 'upload':
                        if dfs.value:
                            row.append("http://stars.aashe.org%s" % dfs.value.url)
                        else:
                            row.append("")
                    else:
                        # long text has to be truncated for excel
                        if dfs.documentation_field.type  == 'long_text':
                            if dfs.value:
                                str_val = dfs.value.replace("\r\n", "\n")
                                if len(str_val) > 32000:
                                    str_val = "%s [TRUNCATED]" % str_val[:32000]
                            else:
                                str_val = ""
                            row.append(smart_str(str_val))
                        
                        else:
                            row.append(smart_str(dfs.value))
        row.append(smart_str(cus.submission_notes))
        csvWriter.writerow(row)

from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import SubmissionSet
from stars.apps.third_parties.models import ThirdParty

cs = CreditSet.objects.get(pk=5)

tp = ThirdParty.objects.get(pk=1)
print "EXPORTING: %s" % tp

snapshot_list = tp.get_snapshots().exclude(institution__id=447)
# print snapshot_list

for cat in cs.category_set.all():
    for sub in cat.subcategory_set.all():
        for c in sub.credit_set.all():
            export_credit_content(c, snapshot_list)