import re

from django.forms import ModelForm
from django import forms
from django.db import models
from django.forms import widgets
from django.forms.util import ErrorList
from django.forms.extras.widgets import SelectDateWidget

from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import Institution, StarsAccount, InstitutionPreferences, STARS_USERLEVEL_CHOICES
from stars.apps.submissions.models import SubmissionSet, ResponsibleParty, Boundary
from stars.apps.third_parties.models import ThirdParty
from stars.apps.accounts.xml_rpc import get_user_by_email

class AdminInstitutionForm(ModelForm):
    """
        This form allows STARS admins to edit an Institution
    """
    class Meta:
        model = Institution
        exclude = ['name', 'aashe_id', 'current_subscription', 'current_submission', 'rated_submission']

#    @staticmethod
    def form_name():
        return u"Institution Form" 
    form_name = staticmethod(form_name)
    
    def __init__(self, *args, **kwargs):
        super(AdminInstitutionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if self.fields[f].widget.__class__.__name__ == "TextInput":
                self.fields[f].widget.attrs.update({'size': 40})
        
class InstitutionContactForm(AdminInstitutionForm):
    """
        A restricted version of the Institution Form, allowing institution admins to edit their Contact info.
    """
    class Meta(AdminInstitutionForm.Meta):
        fields = [  'contact_first_name',
                    'contact_middle_name',
                    'contact_last_name',
                    'contact_title',
                    'contact_department',
                    'contact_phone',
                    'contact_phone_ext',
                    'contact_email',
                    'contact_first_name',
                    'executive_contact_middle_name',
                    'executive_contact_last_name',
                    'executive_contact_title',
                    'executive_contact_department',
                    'executive_contact_email',
                    'executive_contact_address',
                    'executive_contact_city',
                    'executive_contact_state',
                    'executive_contact_zip'
                ]


class AdminEnableInstitutionForm(ModelForm):
    """
        This form allows admin to enable / disable a SubmissionSet
    """    
    class Meta:
        model = Institution
        fields = ['enabled']

class ResponsiblePartyForm(ModelForm):
    
    class Meta:
        model = ResponsibleParty
        exclude = ['institution',]

class MigrateSubmissionSetForm(ModelForm):
    """
        The form to trigger migration for a Submission
        Use the locked field as a confirm checkbox...
    """
    class Meta:
        model = SubmissionSet
        fields = ['is_locked',]
        
    def __init__(self, *args, **kwargs):
        super(MigrateSubmissionSetForm, self).__init__(*args, **kwargs)
        
        self.fields['is_locked'].label = "I am sure I want to migrate?"

class AdminSubmissionSetForm(ModelForm):
    """
        This form allows for editing of a SubmissionSet
    """
    
    class Meta:
        model = SubmissionSet
        exclude = ['institution', 'submission_boundary', 'presidents_letter','reporter_status','pdf_report','score']
        
#    @staticmethod
    def form_name():
        return u"Administer Submission Set Form" 
    form_name = staticmethod(form_name)

    def __init__(self, *args, **kwargs):
        super(AdminSubmissionSetForm, self).__init__(*args, **kwargs)
        user_choices = [('', '----------')] + [(account.user.id, account.user.username) for account in self.instance.institution.starsaccount_set.all()]
        self.fields['registering_user'].choices = user_choices
        self.fields['submitting_user'].choices = user_choices
        self.fields['rating'].choices = [('', '----------')] + [(r.id, r.name) for r in self.instance.creditset.rating_set.all()]

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
                if reviewed and reviewed < submitted :
                    msg = u"Review can't be before submission date."
                    self._errors['date_reviewed'] = ErrorList([msg])
            elif reviewed : # and not submitted
                msg = u"Cannot specify a Review date without a Submission date."
                self._errors['date_reviewed'] = ErrorList([msg])
                del cleaned_data["date_reviewed"]
                
            if deadline and deadline <= registered :
                msg = u"Submission Deadline must be later than registration date."
                self._errors['submission_deadline'] = ErrorList([msg])
            
        return cleaned_data
    
class NotifyUsersForm(ModelForm):
    """
        Does the admin want to notify users of any changes made to their accounts?
    """
    notify_users = forms.BooleanField(label='Notification Preference', required=False, help_text="Users should be sent an e-mail notifying them of changes to their account.")

    class Meta:
        model = InstitutionPreferences
        fields = ['notify_users', ]
    
class AccountForm(forms.Form):
    """
        A form used to identify, add, or edit a user account
    """
    
    email = forms.EmailField(widget=widgets.TextInput(attrs={'size': 40,}))
    userlevel = forms.CharField(label="Role", widget=widgets.Select(choices=STARS_USERLEVEL_CHOICES))
    
#    @staticmethod
    def form_name():
        return u"Administer User Form" 
    form_name = staticmethod(form_name)
         
class EditAccountForm(AccountForm):
    """
        An account form intended for editing an existing account (email field is hidden)
    """
    email = forms.EmailField(widget=widgets.HiddenInput)

class DisabledAccountForm(AccountForm):
    """
        An account form with all fields disabled
    """
    def __init__(self, *args, **kwargs):
        super(DisabledAccountForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({"disabled":"disabled"})
        self.fields['userlevel'].widget.attrs={"disabled":"disabled"}
       
class BoundaryForm(ModelForm):
    """
        This is a form for the Institutional Boundary
    """    
    class Meta:
        model = Boundary
        exclude = ['submissionset',]

class ThirdPartiesForm(ModelForm):
    """
        Institutions can select which orgs to share with
    """
    third_parties = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=ThirdParty.objects.all())
    
    class Meta:
        model = Institution
        fields = []

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:            
            initial = kwargs.setdefault('initial', {})
            initial['third_parties'] = [t.pk for t in kwargs['instance'].third_parties.all()]
        forms.ModelForm.__init__(self, *args, **kwargs)
  
    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)

        # Prepare a 'save_m2m' method for the form,
        old_save_m2m = self.save_m2m
        def save_m2m():
           old_save_m2m()
           instance.third_parties.clear()
           for t in self.cleaned_data['third_parties']:
               instance.third_parties.add(t)
        self.save_m2m = save_m2m

        # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()

        return instance