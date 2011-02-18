from django.forms import ModelForm, Form
from django import forms

from stars.apps.submissions.models import SubmissionInquiry, SubmissionSet, CreditSubmissionInquiry, DataCorrectionRequest

class SubmissionSelectForm(Form):
    
    institution = forms.ModelChoiceField(queryset=SubmissionSet.objects.get_rated(), empty_label="Please Select an Institution's Submission")

class SubmissionInquiryForm(ModelForm):
    
    class Meta:
        model = SubmissionInquiry
        exclude = ['submissionset', 'date']
        
    def __init__(self, *args, **kwargs):
        super(SubmissionInquiryForm, self).__init__(*args, **kwargs)
        
        self.fields['additional_comments'].label = "The following text box may be used for other questions, comments, or suggestions for the STARS Team (not sent to the Institution's STARS Liaison):"
        
class CreditSubmissionInquiryForm(ModelForm):
    
    class Meta:
        model = CreditSubmissionInquiry
        exclude = ['submission_inquiry',]
        
    def __init__(self, creditset=None, *args, **kwargs):
        """ Use a specific creditset to populate the choices """
        
        super(CreditSubmissionInquiryForm, self).__init__(*args, **kwargs)
        
        self.fields['credit'].choices = creditset.get_pulldown_credit_choices()
        
class DataCorrectionRequestForm(ModelForm):
    
    class Meta:
        model = DataCorrectionRequest
        exclude = ['reporting_field', 'object_id', 'content_type', 'user', 'approved']
        
    def __init__(self, creditset=None, *args, **kwargs):
        
        super(DataCorrectionRequestForm, self).__init__(*args, **kwargs)
        
        self.fields['new_value'].label = "New Text:"