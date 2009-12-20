from django.forms import ModelForm

from stars.apps.submissions.models import Payment

class PaymentForm(ModelForm):
    """
        This form allows STARS admins to edit or create a payment record for a given submissionset 
        - an instance with valid submissionset->institution must be specified when form is created.
    """
    class Meta:
        model = Payment
#        exclude = ('submissionset','reason','user')

#    @staticmethod
    def form_name():
        return u"Payment Form" 
    form_name = staticmethod(form_name)
        
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        institution = self.instance.submissionset.institution
        self.fields['user'].choices = [('', '----------')] + [(account.user.id, account.user.username) for account in institution.starsaccount_set.all()]
        self.fields['submissionset'].choices = [('', '----------')] + [(ss.id, ss.creditset) for ss in institution.submissionset_set.all()]

        if self.instance.user:  # ensure the original payee is in the list, no matter what...
            self.add_user(self.instance.user)
            
    def add_user(self, user):
        """ Add the user to the list of users available as payees """
        # Only add the user if they are not already there...
        for id, name in self.fields['user'].choices:
            if id == user.id:
                return
        # assert:  user is not yet listed in the choices.
        self.fields['user'].choices.append((user.id, user.username))
        
        
