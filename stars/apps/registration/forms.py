from django import forms
from django.forms import ModelForm
from django.forms.util import ErrorList

from stars.apps.institutions.models import (Institution, RespondentSurvey,
                                            RegistrationSurvey, Subscription)
from stars.apps.registration.utils import is_canadian_zipcode, is_usa_zipcode
from stars.apps.registration.models import ValueDiscount

class WriteInInstitutionForm(forms.Form):
    """
        A form for an institution that we don't have stored yet
    """
    institution_name = forms.CharField(max_length=255, required=True)

    def __init__(self, *args, **kwargs):
        super(WriteInInstitutionForm, self).__init__(*args, **kwargs)
        self.fields['institution_name'].widget.attrs['size'] = 60

class RegistrationSchoolChoiceForm(forms.Form):
    """
        A form for selecting an institution form institutionnames
    """
    aashe_id = forms.IntegerField()

#    class Meta:
#        model = Institution
#        fields = ['aashe_id']

    def __init__(self, *args, **kwargs):
        super(RegistrationSchoolChoiceForm, self).__init__(*args, **kwargs)
        self.fields['aashe_id'].label = "Institution"

class RegistrationForm(ModelForm):
    """
        Contact Information Form
    """
    #terms_of_service = forms.BooleanField(label="I agree to the terms of service", required=True)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['contact_first_name'].label = "First Name"
        self.fields['contact_middle_name'].label = "Middle Name"
        self.fields['contact_last_name'].label = "Last Name"
        self.fields['contact_title'].label = "Title"
        self.fields['contact_department'].label = "Department/Office"
        self.fields['contact_phone'].label = "Phone"
        self.fields['contact_email'].label = "Email"
        self.fields['executive_contact_first_name'].label = "First Name"
        self.fields['executive_contact_middle_name'].label = "Middle Name"
        self.fields['executive_contact_last_name'].label = "Last Name"
        self.fields['executive_contact_title'].label = "Title"
        self.fields['executive_contact_department'].label = "Department/Office"
        self.fields['executive_contact_email'].label = "Email"

        self.fields['executive_contact_first_name'].required = True
        self.fields['executive_contact_middle_name'].required = False
        self.fields['executive_contact_last_name'].required = True
        self.fields['executive_contact_title'].required = True
        self.fields['executive_contact_department'].required = True
        self.fields['executive_contact_email'].required = True

    class Meta:
        model = Institution
        fields =    [
                        'contact_first_name',
                        'contact_middle_name',
                        'contact_last_name',
                        'contact_title',
                        'contact_department',
                        'contact_phone',
                        'contact_email',
                        'executive_contact_first_name',
                        'executive_contact_middle_name',
                        'executive_contact_last_name',
                        'executive_contact_title',
                        'executive_contact_department',
                        'executive_contact_email',
                    ]

    def clean(self):
        cleaned_data = self.cleaned_data

        # confirm that the contact email and the executive email are not the same
        if cleaned_data.has_key("contact_email") and cleaned_data.has_key("executive_contact_email"):
            contact = cleaned_data.get("contact_email")
            executive = cleaned_data.get("executive_contact_email")

            if contact == executive:
                msg = u"Oops, you've entered the same information for both the primary and executive contact. Please make sure these contacts are two different individuals at your institution."
                self._errors["executive_contact_email"] = ErrorList([msg])

                # The executive field is no longer valid
                del cleaned_data["executive_contact_email"]

        return cleaned_data

class DataCollectorRegistrationForm(ModelForm):
    """
        Contact Information Form with just the liaison
    """

    def __init__(self, *args, **kwargs):
        super(DataCollectorRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['contact_first_name'].label = "First Name"
        self.fields['contact_middle_name'].label = "Middle Name"
        self.fields['contact_last_name'].label = "Last Name"
        self.fields['contact_title'].label = "Title"
        self.fields['contact_department'].label = "Department/Office"
        self.fields['contact_phone'].label = "Phone"
        self.fields['contact_email'].label = "Email"

    class Meta:
        model = Institution
        fields =    [
                        'contact_first_name',
                        'contact_middle_name',
                        'contact_last_name',
                        'contact_title',
                        'contact_department',
                        'contact_phone',
                        'contact_email',
                    ]

PARTICIPATION_CHOICES = (
                            ("participant", "STARS Participant"),
                            ("respondent", "Survey Respondent"),
                        )

class ParticipationLevelForm(forms.Form):
    level = forms.fields.ChoiceField(widget=forms.widgets.RadioSelect,
                                     choices=PARTICIPATION_CHOICES)

class PaymentOptionsForm(forms.Form):
    """
        Youse can pay me now, or youse can pay me later.
    """
    pay_when = forms.ChoiceField(
        choices=[
            (Subscription.PAY_NOW, 'Pay now'),
            (Subscription.PAY_LATER, 'Pay later (i.e., be billed)')],
        widget=forms.RadioSelect())

class PromoForm(forms.ModelForm):
    """
        A form with a promo code field.
    """
    class Meta:
        model = Subscription
        fields = ['promo_code']

    promo_code = forms.CharField(max_length=16, required=False)

    def clean_promo_code(self):
        data = self.cleaned_data['promo_code']
        if data == "":
            return None

        try:
            ValueDiscount.objects.get_current().get(code=data)
        except ValueDiscount.DoesNotExist:
            raise forms.ValidationError(
                "Sorry, but that's not a valid promo code.")

        return data

class PayLaterForm(PromoForm):
    pass


class PayNowForm(PromoForm):
    """
        Credit Card Payment form
    """
    name_on_card = forms.CharField(max_length=64)
    card_number = forms.CharField(
        max_length=17, widget=forms.TextInput(attrs={'autocomplete': 'off',}))
    exp_month = forms.CharField(max_length=2, initial='mm')
    exp_year = forms.CharField(max_length=4, initial='yyyy')
    cv_code = forms.CharField(
        max_length=3, label='CV Code',
        help_text='This is the 3-digit code on the back of your card',
        widget=forms.TextInput(attrs={'autocomplete': 'off',}))
    billing_address = forms.CharField(max_length=128)
    billing_address_line_2 = forms.CharField(max_length=128, required=False)
    billing_city = forms.CharField(max_length=32)
    billing_state = forms.CharField(max_length=2)
    billing_zipcode = forms.CharField(max_length=7, label='Billing ZIP code')
    promo_code = forms.CharField(max_length=16, required=False)

    def clean_exp_month(self):
        data = self.cleaned_data['exp_month']
        error_text = "Please enter a number between 1 and 12"

        if not self.is_numeric(data):
            raise forms.ValidationError(error_text)
        month = int(data)
        if month > 12 or month < 0:
            raise forms.ValidationError(error_text)

        return data

    def clean_exp_year(self):
        data = self.cleaned_data['exp_year']
        error_text = "Please enter a valid year"

        if not self.is_numeric(data):
            raise forms.ValidationError(error_text)

        return data

    def clean_billing_zipcode(self):
        data = self.cleaned_data['billing_zipcode']
        error_text = "Please enter a valid US or Canadian zip code"

        if not is_usa_zipcode(data) and not is_canadian_zipcode(data):
            raise forms.ValidationError(error_text)

        return data

    def is_numeric(self, data):
        """ Helper function to indicate if data is numeric. """
        try:
            number = int(data)
        except:
            return False
        return True

class RegistrationSurveyForm(ModelForm):

    class Meta:
        model = RegistrationSurvey
        fields = ['source', 'reasons', 'other', 'primary_reason', 'enhancements']

    def __init__(self, *args, **kwargs):
        from stars.apps.institutions.models import RegistrationReason
        super(RegistrationSurveyForm, self).__init__(*args, **kwargs)
        choices = []
        for r in RegistrationReason.objects.all():
            if r.title != "Other" and r.title != "No reason was primary":
                choices.append((r.id, r.title))
        self.fields['reasons'].widget = forms.CheckboxSelectMultiple(choices=choices)
        self.fields['reasons'].help_text = "Select all that apply"
        self.fields['reasons'].label = "The reason(s) your institution registered for STARS were to:"
        self.fields['primary_reason'].label = "Which of the above reasons, if any, was the primary reason your institution registered for STARS?"

class RespondentRegistrationSurveyForm(ModelForm):

    class Meta:
        model = RespondentSurvey
        fields = ['source', 'reasons', 'other', 'potential_stars']

    def __init__(self, *args, **kwargs):
        super(RespondentRegistrationSurveyForm, self).__init__(*args, **kwargs)

        from stars.apps.institutions.models import RespondentRegistrationReason
        choices = []
        for r in RespondentRegistrationReason.objects.all():
#            if r.title != "Other" and r.title != "No reason was primary":
            choices.append((r.id, r.title))

        self.fields['reasons'].widget = forms.CheckboxSelectMultiple(choices=choices)
        self.fields['reasons'].help_text = "Select all that apply"
        self.fields['reasons'].label = "The reason(s) your institution registered for the CSDC were to:"
