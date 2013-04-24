from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm

from stars.apps.institutions.models import StarsAccount

class LoginForm(AuthenticationForm):
    """ Extends the AuthenticationForm to use longer usernames """
    
    username = forms.CharField(label="Email", max_length=100)

class TOSForm(ModelForm):
    """
        Form that allows users to check the Terms of Service
    """
    terms_of_service = forms.BooleanField(label='I agree to the terms of service', required=True)
    
    class Meta:
        model = StarsAccount
        fields = ['terms_of_service',]
