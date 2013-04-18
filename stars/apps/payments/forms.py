from django import forms

from utils import is_canadian_zipcode, is_usa_zipcode
from credit_card import CreditCardPaymentProcessor, CreditCardProcessingError


class PayLaterForm(forms.Form):

    confirm = forms.BooleanField(
         label="Please bill me and I will pay later.",
         required=False,
         widget=forms.CheckboxInput(attrs={'onchange':
                                           'togglePayment(this);'}))


class PaymentForm(forms.Form):
    """
        Credit Card Payment form

        Will run the payment if it's indicated with the kwargs: 'process'

        PaymentForm(process=True...)

        If processing then user and amount values must be specified too
    """
    name_on_card = forms.CharField(max_length=64)
    card_number = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    exp_month = forms.CharField(max_length=2, initial='mm')
    exp_year = forms.CharField(max_length=4, initial='yyyy')
    cv_code = forms.CharField(
        max_length=3,
        label='CV Code',
        help_text='This is the 3-digit code on the back of your card',
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    billing_address = forms.CharField(max_length=128)
    billing_address_line_2 = forms.CharField(max_length=128, required=False)
    billing_city = forms.CharField(max_length=32)
    billing_state = forms.CharField(max_length=2)
    billing_zipcode = forms.CharField(max_length=7, label='Billing ZIP code')

    def __init__(self, *args, **kwargs):
        """
            if kwargs has "process" then the clean
            method will process the payment
        """
        self.process = kwargs.pop('process', False)
        self.amount = kwargs.pop('amount', None)
        self.user = kwargs.pop('user', None)
        self.contact_info = kwargs.pop('contact_info', None)
        self.invoice_num = kwargs.pop('invoice_num', None)
        super(PaymentForm, self).__init__(*args, **kwargs)

    def get_amount(self):
        return self.amount

    def clean(self):
        cleaned_data = self.cleaned_data
        if self.process:
            self.process_payment()
        return cleaned_data

    def process_payment(self):
        cc = CreditCardPaymentProcessor()
        try:
            result = cc.process_payment_form(self.contact_info,
                                             self.amount,
                                             self.user,
                                             self,
                                             self.invoice_num,
                                             product_name=None)
        except CreditCardProcessingError, e:
            raise forms.ValidationError(e)
        if not result['cleared']:
            raise forms.ValidationError(result['msg'])

        self.confirmation = result['conf']
        return self.confirmation

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
            __ = int(data)
        except:
            return False
        return True


class PaymentFormWithPayLater(PaymentForm):

    pay_later = forms.BooleanField(
        label="Please bill me and I will pay later.",
        required=False,
        widget=forms.CheckboxInput(attrs={'onchange':
                                          'togglePayment(this);'}))

    def clean(self):

        if self.cleaned_data['pay_later']:
            # When pay_later is selected, the only error we care about
            # is discount_code.
            for error in self._errors.keys():
                if error != 'discount_code':
                    del self._errors[error]

            return self.cleaned_data

        else:  # pay now
            # PaymentForm.clean is where the payment is processed:
            return super(PaymentFormWithPayLater, self).clean()
