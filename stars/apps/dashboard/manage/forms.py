import re

from django.forms import ModelForm
from django import forms
from django.forms import widgets
from django.forms.util import ErrorList
from django.forms.extras.widgets import SelectDateWidget

from stars.apps.credits.models import *
from stars.apps.institutions.models import *
from stars.apps.submissions.models import *
from stars.apps.auth.xml_rpc import get_user_by_email

class AdminInstitutionForm(ModelForm):
    """
        This form allows STARS admins to edit an Institution
    """
    class Meta:
        model = Institution
        exclude = ['name', 'aashe_id', ]

#    @staticmethod
    def form_name():
        return u"Institution Form" 
    form_name = staticmethod(form_name)
        
class InstitutionContactForm(AdminInstitutionForm):
    """
        A restricted version of the Institution Form, allowing institution admins to edit their Contact info.
    """
    class Meta(AdminInstitutionForm.Meta):
        exclude = ['name', 'aashe_id', 'enabled',]


class AdminSubmissionSetForm(ModelForm):
    """
        This form allows for editing of a SubmissionSet
    """
    
    date_registered = forms.DateField(widget=SelectDateWidget(required=False))
    date_submitted = forms.DateField(widget=SelectDateWidget(required=False), required=False)
    date_reviewed = forms.DateField(widget=SelectDateWidget(required=False), required=False)
    submission_deadline = forms.DateField(widget=SelectDateWidget(required=False))
    
    class Meta:
        model = SubmissionSet
        exclude = ['institution']
        
#    @staticmethod
    def form_name():
        return u"Administer Submission Set Form" 
    form_name = staticmethod(form_name)

    def __init__(self, *args, **kwargs):
        super(AdminSubmissionSetForm, self).__init__(*args, **kwargs)
        self.fields['registering_user'].choices = [('', '----------')] + [(account.user.id, account.user.username) for account in self.instance.institution.starsaccount_set.all()]
        self.fields['submitting_user'].choices = [('', '----------')] + [(account.user.id, account.user.username) for account in self.instance.institution.starsaccount_set.all()]

    def clean(self):
        """ Validate date ordering: registered < submitted < reviewed and registered < deadline """    
        cleaned_data = self.cleaned_data
        registered = cleaned_data.get('date_registered')
        submitted = cleaned_data.get('date_submitted')
        reviewed = cleaned_data.get('date_reviewed')
        deadline = cleaned_data.get('submission_deadline')
        
        if not registered : # this check is handled by normal validation... but to be sure
            msg = u"Registration date is required."
            self._errors['date_registered'] = ErrorList([msg])
        else:
            if submitted :
                if submitted <= registered :
                    msg = u"Submission date must be later than registration date."
                    self._errors['date_submitted'] = ErrorList([msg])            
                if reviewed and reviewed <= submitted :
                    msg = u"Review date must be later than submission date."
                    self._errors['date_reviewed'] = ErrorList([msg])
            elif reviewed : # and not submitted
                msg = u"Cannot specify a Review date without a Submission date."
                self._errors['date_reviewed'] = ErrorList([msg])
                del cleaned_data["date_reviewed"]
                
            if deadline and deadline <= registered :
                msg = u"Submission Deadline must be later than registration date."
                self._errors['submission_deadline'] = ErrorList([msg])
            
        return cleaned_data
    
class AccountForm(forms.Form):
    """
        A form used to identify, add, or edit a user account
    """
    
    email = forms.EmailField()
    userlevel = forms.CharField(widget=widgets.Select(choices=STARS_USERLEVEL_CHOICES))
    
#    @staticmethod
    def form_name():
        return u"Administer User Form" 
    form_name = staticmethod(form_name)

    """
    def clean_email():
        email = self.cleaned_data['email']
        user_list = get_user_by_email(email)
        if not user_list:
            raise forms.ValidationError("Sorry, no AASHE user has that email.")
        return email
    """