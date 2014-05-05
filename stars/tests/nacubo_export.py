"""

    Export excel documents for nacubo

    institution columns


        Name of College/University
        Carnegie Classification:  Type of institution
        Classification - Control - public or private
        FTE
        Year of Data
        Gross Sq Feet of Year that Data given 

    2.0 columns:

        MMBTU  consumed OP8
        Electrical Possible Kw - given the gird purchase consumption - verify if available in KW as that is usually what campus invoices state
        Water - OP 26 total water used in gallons
        Carbon Footprint - Scope 1 and 2 ft squared o green energy metric tons of carbon dioxide
        Waste - OP 22  - given out as Tons

    1.2 columns:
"""

# from stars.apps.third_parties.utils import UnicodeWriter
import csv

from stars.apps.credits.models import DocumentationField
from stars.apps.submissions.models import (
                                           SubmissionSet,
                                           NumericSubmission,
                                           DateSubmission,
                                           ChoiceSubmission,
                                           CreditUserSubmission
                                           )
first_columns = [
                 "Name",
                 "Institution Type",
                 "FTE",
#                  "Gross Sq Feet"
                 ]

outfile = open("nacubo/2.0.csv", 'wb')
# csvWriter = UnicodeWriter(outfile)
csvWriter = csv.writer(outfile)

headers = []
headers.extend(first_columns)

field_list = [

                ("Institution Control", 4230, ChoiceSubmission),

                # OP-8
                ("OP-8 Performance Year", 3612, DateSubmission),
                ("Gross Sq Feet (PY)", 2810, NumericSubmission),
                ("MMBTU Consumed (PY)", 2811, NumericSubmission),
                ("Grid-purchased electricity for buildings (PY)", 3603, NumericSubmission),
                ("OP-8 Baseline Year", 3616, DateSubmission),
                ("MMBTU Consumed (BY)", 2813, NumericSubmission),
                ("Grid-purchased electricity for buildings (BY)", 3614, NumericSubmission),
                ("Gross Sq Feet (BY)", 2812, NumericSubmission),

                # OP 26
                ("OP-26 Performance Year", 3864, DateSubmission),
                ("Total Water Use (PY)", 3030, NumericSubmission),
                ("OP-26 Baseline Year", 3866, DateSubmission),
                ("Total Water Use (BY)", 3031, NumericSubmission),

                # OP 1
                # "Carbon Footprint",
                ("OP-1 Performance Year", 3646, DateSubmission),
                ("Scope 1 GHG emissions from stationary combustion (PY)", 3627, NumericSubmission),
                ("Scope 1 GHG emissions from other sources (PY)", 3628, NumericSubmission),
                ("Scope 2 GHG emissions from purchased electricity (PY)", 3629, NumericSubmission),
                ("Scope 2 GHG emissions from other sources (PY)", 3630, NumericSubmission),
                ("OP-1 Baseline Year", 3658, DateSubmission),
                ("Scope 1 GHG emissions from stationary combustion (BY),", 3648, NumericSubmission),
                ("Scope 1 GHG emissions from other sources (BY)", 3649, NumericSubmission),
                ("Scope 2 GHG emissions from purchased electricity (BY)", 3650, NumericSubmission),
                ("Scope 2 GHG emissions from other sources (BY)", 3651, NumericSubmission),

                # Waste
                # OP 22
                ("OP-22 Performance Year", 3841, DateSubmission),
                ("Waste - Recycled (PY)", 2981, NumericSubmission),
                ("Waste - Composted (PY)", 2980, NumericSubmission),
                ("Waste - Reused (PY)", 3827, NumericSubmission),
                ("Waste - Garbage (PY)", 2979, NumericSubmission),
                ("OP-22 Baseline Year", 3843, DateSubmission),
                ("Waste - Recycled (BY)", 2984, NumericSubmission),
                ("Waste - Composted (BY)", 2983, NumericSubmission),
                ("Waste - Reused (BY)", 3828, NumericSubmission),
                ("Waste - Garbage (BY)", 2982, NumericSubmission),
                ]

for f in field_list:
    units = ""
    if f[2] == NumericSubmission:
        units = " [%s]" % DocumentationField.objects.get(pk=f[1]).units
    headers.append("%s%s" % (f[0], units))
csvWriter.writerow(headers)

print "# of 2.0 Institutions"
print SubmissionSet.objects.filter(status="r").filter(creditset=6).count()

for ss in SubmissionSet.objects.filter(status="r").filter(creditset=6):
    row = [
       ss.institution.name,
       ss.institution.profile.carnegie_class,
       # control - we don't have this in the ISS
       ss.institution.profile.enrollment_fte
       ]

    for f in field_list:
        klass = f[2]
        df = DocumentationField.objects.get(pk=f[1])

        cus = CreditUserSubmission.objects.filter(subcategory_submission__category_submission__submissionset=ss)
        cus = cus.get(credit=df.credit)
        val = klass.objects.filter(documentation_field=df)
        val = val.get(credit_submission_id=cus.id).value

        row.append(val)

    csvWriter.writerow(row)

outfile.close()

print "# of 1.2 Institutions"
print SubmissionSet.objects.filter(status="r").filter(creditset=5).count()

