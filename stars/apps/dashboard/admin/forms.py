from django.forms import ModelForm

from stars.apps.submissions.models import Payment

class PaymentForm(ModelForm):
    
    class Meta:
        model = Payment
        
        exclude = ('submissionset','reason','user')