from django import forms
from django.forms import widgets
from django.forms import ModelForm
from django.forms.util import ErrorList

from aashe.issdjango.models import Organizations
from stars.apps.institutions.models import (Institution,
                                            RegistrationSurvey,
                                            RespondentSurvey)
from stars.apps.registration.models import (ExpiredDiscountCodeError,
                                            InvalidDiscountCodeError,
                                            get_current_discount)
from stars.apps.payments.forms import PaymentFormWithPayLater


class RegistrationPaymentForm(PaymentFormWithPayLater):
    discount_code = forms.CharField(max_length=16, required=False)

    def __init__(self, *args, **kwargs):
        self.discount = None
        super(RegistrationPaymentForm, self).__init__(*args, **kwargs)

    def get_amount(self):
        if self.discount:
            return self.discount.apply(self.amount)
        else:
            return self.amount

    def clean_discount_code(self):
        discount_code = self.cleaned_data['discount_code']

        if discount_code:
            try:
                self.discount = get_current_discount(code=discount_code)
            except InvalidDiscountCodeError:
                raise forms.ValidationError("Invalid Discount Code")
            except ExpiredDiscountCodeError:
                raise forms.ValidationError("Expired Discount Code")

        return discount_code


class WriteInInstitutionForm(forms.Form):
    """
        A form for an institution that we don't have stored yet
    """
    institution_name = forms.CharField(max_length=255, required=True)

    def __init__(self, *args, **kwargs):
        super(WriteInInstitutionForm, self).__init__(*args, **kwargs)
        self.fields['institution_name'].widget.attrs['size'] = 60


class SelectSchoolForm(forms.Form):
    """
    A form for selecting an Organization from Organization names.

    Organizations limited to ORG_TYPES and COUNTRIES listed.
    """
    aashe_id = forms.IntegerField()

    ORG_TYPES = ('I',
                 'Four Year Institution',
                 'Two Year Institution',
                 'Graduate Institution',
                 'System Office')
    COUNTRIES = ('Canada', 'United States of America')

    def __init__(self, *args, **kwargs):
        super(SelectSchoolForm, self).__init__(*args, **kwargs)
        self.institution_list = self.get_institution_choices()
        self.fields['aashe_id'].label = "Institution"
        self.fields['aashe_id'].widget = widgets.Select(
            choices=self.institution_list,
            attrs={
                'style': "width: 700px",
                'id': "school_select"})

    def get_institution_choices(self):
        institution_choices = []

        for org in Organizations.objects.filter(
                org_type__in=self.ORG_TYPES,
                country__in=self.COUNTRIES).order_by('org_name'):

            choice_label = org.org_name
            if org.city and org.state:
                choice_label = ", ".join((choice_label, org.city, org.state))

            institution_choices.append((org.account_num, choice_label))

        return institution_choices


class ContactForm(ModelForm):
    """
        Contact form that takes the option to have show executive contact
        fields
    """
    class Meta:
        model = Institution
        fields = ['contact_first_name',
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
                  'executive_contact_email']

    def __init__(self, *args, **kwargs):

        super(ContactForm, self).__init__(*args, **kwargs)
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
        self.fields['executive_contact_department'].label = (
            "Department/Office")
        self.fields['executive_contact_email'].label = "Email"

        self.fields['executive_contact_first_name'].required = True
        self.fields['executive_contact_middle_name'].required = False
        self.fields['executive_contact_last_name'].required = True
        self.fields['executive_contact_title'].required = True
        self.fields['executive_contact_department'].required = True
        self.fields['executive_contact_email'].required = True

    def clean(self):
        cleaned_data = self.cleaned_data

        if ("contact_email" in cleaned_data.keys() and
            "executive_contact_email" in cleaned_data.keys()):

            contact = cleaned_data.get("contact_email")
            executive = cleaned_data.get("executive_contact_email")

            if contact == executive:
                msg = ("Oops, you've entered the same information for both"
                       " the primary and executive contact. Please make"
                       " sure these contacts are two different individuals"
                       " at your institution.")
                self._errors["executive_contact_email"] = ErrorList([msg])

                # The executive field is no longer valid
                del cleaned_data["executive_contact_email"]

        return cleaned_data


PARTICIPATION_CHOICES = (("participant", "STARS Participant"),
                         ("respondent", "Survey Respondent"),)


class ParticipationLevelForm(forms.Form):
    level = forms.fields.ChoiceField(widget=forms.widgets.RadioSelect,
                                     choices=PARTICIPATION_CHOICES)


class RegistrationSurveyForm(ModelForm):

    class Meta:
        model = RegistrationSurvey
        fields = ['source', 'reasons', 'other',
                  'primary_reason', 'enhancements']

    def __init__(self, *args, **kwargs):
        from stars.apps.institutions.models import RegistrationReason
        super(RegistrationSurveyForm, self).__init__(*args, **kwargs)
        choices = []
        for r in RegistrationReason.objects.all():
            if r.title != "Other" and r.title != "No reason was primary":
                choices.append((r.id, r.title))
        self.fields['reasons'].widget = forms.CheckboxSelectMultiple(
            choices=choices)
        self.fields['reasons'].help_text = "Select all that apply"
        self.fields['reasons'].label = ("The reason(s) your institution "
                                        "registered for STARS were to:")
        self.fields['primary_reason'].label = (
            "Which of the above reasons, if any, was the primary reason "
            "your institution registered for STARS?")


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

        self.fields['reasons'].widget = forms.CheckboxSelectMultiple(
            choices=choices)
        self.fields['reasons'].help_text = "Select all that apply"
        self.fields['reasons'].label = ("The reason(s) your institution "
                                        "registered for the CSDC were to:")
