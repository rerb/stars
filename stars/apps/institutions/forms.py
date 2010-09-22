from django.forms import ModelForm, Form
from django import forms

from stars.apps.submissions.models import SubmissionEnquiry, SubmissionSet, CreditSubmissionEnquiry

class SubmissionSelectForm(Form):
    
    institution = forms.ModelChoiceField(queryset=SubmissionSet.objects.get_rated(), empty_label="Please Select an Institution's Submission")

class SubmissionEnquiryForm(ModelForm):
    
    class Meta:
        model = SubmissionEnquiry
        exclude = ['submissionset', 'date']
        
class CreditSubmissionEnquiryForm(ModelForm):
    
    class Meta:
        model = CreditSubmissionEnquiry
        exclude = ['submission_enquiry',]
        
    def __init__(self, creditset=None, *args, **kwargs):
        """ Use a specific creditset to populate the choices """
        
        super(CreditSubmissionEnquiryForm, self).__init__(*args, **kwargs)
        
        self.fields['credit'].choices = creditset.get_pulldown_credit_choices()
        