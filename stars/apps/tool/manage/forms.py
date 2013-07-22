from django import forms
from django.forms import ModelForm
from django.forms import widgets
from django.forms.util import ErrorList

from stars.apps.helpers.forms.forms import LocalizedModelFormMixin
from stars.apps.institutions.models import (Institution,
                                            InstitutionPreferences,
                                            STARS_USERLEVEL_CHOICES,
                                            Subscription)
from stars.apps.registration.models import ValueDiscount
from stars.apps.payments.utils import is_canadian_zipcode, is_usa_zipcode
from stars.apps.submissions.models import (SubmissionSet, ResponsibleParty,
                                           Boundary)
from stars.apps.third_parties.models import ThirdParty


class AdminInstitutionForm(LocalizedModelFormMixin, ModelForm):
    """
        This form allows STARS admins to edit an Institution
    """
    class Meta:
        model = Institution
        exclude = ['name', 'aashe_id', 'current_subscription',
                   'current_submission', 'rated_submission']

    def __init__(self, *args, **kwargs):
        super(AdminInstitutionForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if self.fields[f].widget.__class__.__name__ == "TextInput":
                self.fields[f].widget.attrs.update({'size': 40})


class ParticipantContactForm(AdminInstitutionForm):
    """
        A restricted version of the Institution Form, allowing
        institution admins to edit their Contact info.
    """
    class Meta(AdminInstitutionForm.Meta):
        fields = ['contact_first_name',
                  'contact_middle_name',
                  'contact_last_name',
                  'contact_title',
                  'contact_department',
                  'contact_phone',
                  'contact_phone_ext',
                  'contact_email',
                  'executive_contact_first_name',
                  'executive_contact_middle_name',
                  'executive_contact_last_name',
                  'executive_contact_title',
                  'executive_contact_department',
                  'executive_contact_email']

    def __init__(self, *args, **kwargs):
        super(ParticipantContactForm, self).__init__(*args, **kwargs)

        self.fields['executive_contact_first_name'].required = True
        self.fields['executive_contact_middle_name'].required = True
        self.fields['executive_contact_title'].required = True
        self.fields['executive_contact_department'].required = True
        self.fields['executive_contact_email'].required = True


class RespondentContactForm(AdminInstitutionForm):
    """
        A restricted version of the Institution Form, allowing
        institution admins to edit their Contact info.
    """
    class Meta(AdminInstitutionForm.Meta):
        fields = ['contact_first_name',
                  'contact_middle_name',
                  'contact_last_name',
                  'contact_title',
                  'contact_department',
                  'contact_phone',
                  'contact_phone_ext',
                  'contact_email']


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
        exclude = ['institution']


class MigrateSubmissionSetForm(ModelForm):
    """
        The form to trigger migration for a Submission
        Use the locked field as a confirm checkbox...
    """
    class Meta:
        model = SubmissionSet
        fields = ['is_locked']

    def __init__(self, *args, **kwargs):
        super(MigrateSubmissionSetForm, self).__init__(*args, **kwargs)

        self.fields['is_locked'].label = (
            'Check here to confirm your wish to migrate.')


class AdminSubmissionSetForm(LocalizedModelFormMixin, ModelForm):
    """
        This form allows for editing of a SubmissionSet
    """

    class Meta:
        model = SubmissionSet
        exclude = ['institution', 'submission_boundary',
                   'presidents_letter', 'reporter_status', 'pdf_report',
                   'score']

    def form_name():
        return u"Administer Submission Set Form"
    form_name = staticmethod(form_name)

    def __init__(self, *args, **kwargs):
        super(AdminSubmissionSetForm, self).__init__(*args, **kwargs)
        user_choices = ([('', '----------')] +
                        [(account.user.id, account.user.username) for account
                         in self.instance.institution.starsaccount_set.all()])
        self.fields['registering_user'].choices = user_choices
        self.fields['submitting_user'].choices = user_choices
        self.fields['rating'].choices = (
            [('', '----------')] +
            [(r.id, r.name) for r in self.instance.creditset.rating_set.all()])

    def clean(self):
        """ Validate date ordering: registered < submitted < reviewed
        and registered < deadline"""
        cleaned_data = self.cleaned_data
        registered = cleaned_data.get('date_registered')
        submitted = cleaned_data.get('date_submitted')
        reviewed = cleaned_data.get('date_reviewed')

        if not registered:  # this check is handled by normal
                            # validation... but to be sure
            msg = u"Registration date is required."
            self._errors['date_registered'] = ErrorList([msg])
        else:
            if submitted:
                if submitted <= registered:
                    msg = (u"Submission date must be later than "
                           u"registration date.")
                    self._errors['date_submitted'] = ErrorList([msg])
                if reviewed and reviewed < submitted:
                    msg = u"Review can't be before submission date."
                    self._errors['date_reviewed'] = ErrorList([msg])
            elif reviewed:  # and not submitted
                msg = (u"Cannot specify a Review date without a "
                       u"Submission date.")
                self._errors['date_reviewed'] = ErrorList([msg])
                del cleaned_data["date_reviewed"]

        return cleaned_data


class NotifyUsersForm(ModelForm):
    """
        Does the admin want to notify users of any changes made to
        their accounts?
    """
    notify_users = forms.BooleanField(
        label='Notification Preference',
        required=False,
        help_text="Users should be sent an e-mail notifying them of "
                  "changes to their account.")

    class Meta:
        model = InstitutionPreferences
        fields = ['notify_users', ]


class AccountForm(forms.Form):
    """
        A form used to add and edit a user account.

        When editing an account, the email field is readonly.
    """
    email = forms.EmailField(widget=widgets.TextInput(attrs={'size': 40}))
    userlevel = forms.CharField(
        label="Role",
        widget=widgets.Select(choices=STARS_USERLEVEL_CHOICES))

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        if 'email' in self.initial:
            self.fields['email'].widget.attrs['readonly'] = True

    def clean_email(self):
        """
            Guards against nasty POSTs that try to change the email.
        """
        try:
            return self.initial['email']
        except KeyError:
            return self.cleaned_data.get('email', None)


class DisabledAccountForm(AccountForm):
    """
        An account form with all fields disabled
    """
    def __init__(self, *args, **kwargs):
        super(DisabledAccountForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({"disabled": "disabled"})
        self.fields['userlevel'].widget.attrs = {"disabled": "disabled"}


class BoundaryForm(LocalizedModelFormMixin, ModelForm):
    """
        This is a form for the Institutional Boundary
    """
    class Meta:
        model = Boundary
        exclude = ['submissionset']


class ThirdPartiesForm(ModelForm):
    """
        Institutions can select which orgs to share with
    """
    third_parties = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=ThirdParty.objects.all(),
        required=False)

    class Meta:
        model = Institution
        fields = []

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            initial = kwargs.setdefault('initial', {})
            initial['third_parties'] = [t.pk for t in
                                        kwargs['instance'].third_parties.all()]
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


class PaymentOptionsForm(forms.Form):
    """
        Youse can pay me now, or youse can pay me later.
    """
    pay_when = forms.ChoiceField(
        choices=[
            (Subscription.PAY_NOW, 'Pay now, by credit card'),
            (Subscription.PAY_LATER, 'Pay later (i.e., be billed)')],
        widget=forms.RadioSelect(),
        label='')


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
        max_length=17, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    exp_month = forms.CharField(max_length=2, initial='mm')
    exp_year = forms.CharField(max_length=4, initial='yyyy')
    cv_code = forms.CharField(
        max_length=3, label='CV Code',
        help_text='This is the 3-digit code on the back of your card',
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
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
            _ = int(data)
        except:
            return False
        return True
