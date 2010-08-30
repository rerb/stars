# Sample platypus document
# From the FAQ at reportlab.org/oss/rl-toolkit/faq/#1.1

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.platypus.doctemplate import NextPageTemplate 
from reportlab.platypus.flowables import PageBreak

from stars.apps.institutions.pdf.styles import getSTARSStyleSheet
from stars.apps.institutions.models import * # required for execfile management func
from stars.apps.submissions.models import SubmissionSet

ss = SubmissionSet.objects.get(pk=82)

PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]
styles = getSTARSStyleSheet()

blue = (.21, .37, .56)
dark_blue = (.09, .21, .36)

def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.setFillColorRGB(*dark_blue) 
    canvas.setFont('Times-Bold',16)
    canvas.drawString(inch, PAGE_HEIGHT-108, ss.institution.name)
    
    canvas.setFillColorRGB(*blue)
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch,"%s STARS Report" % ss.institution.name)
    canvas.restoreState()
    
def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch,"Page %d / %s STARS Report" % (doc.page, ss.institution.name))
    canvas.restoreState()
    
def go():
    doc = SimpleDocTemplate("public_report.pdf")
    Story = [PageBreak()]
    # Story = [Spacer(1,2*inch)]
    p_style = styles["Normal"]
    cat_style = styles['Category']
    sub_style = styles['Subcategory']
    cred_style = styles['Credit']
    for cat in ss.categorysubmission_set.all():
        p = Paragraph(cat.category.title, cat_style)
        Story.append(p)
        for sub in cat.subcategorysubmission_set.all():
            p = Paragraph(sub.subcategory.title, sub_style)
            Story.append(p)
            for cs in sub.creditusersubmission_set.all():
                p = Paragraph("%s: %s" % (cs.credit.get_identifier(), cs.credit.title), cred_style)
                Story.append(p)
        Story.append(PageBreak())
    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    
if __name__ == "__main__":
    go()
