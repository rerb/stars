from django.forms import ModelForm
from django.forms.util import ErrorList
from django.contrib.auth.models import User

from models import WatchdogContact

class AdminWatchdogContactForm(ModelForm):
    """
        This form allows for editing of a Watchdog Contact
    """    
    class Meta:
        model = WatchdogContact

    def __init__(self, *args, **kwargs):
        super(AdminWatchdogContactForm, self).__init__(*args, **kwargs)
        staff = User.objects.filter(is_staff=True) 
        self.fields['user'].choices = [('', '----------')] + [(user.id, user.email) for user in staff]

    def clean(self):
        """ Only staff members are valid watchdog contacts """    
        cleaned_data = self.cleaned_data
        user = cleaned_data.get('user')
        
        if not user.is_staff:
            msg = u"Permission Denied.  %s may not receive Watchdog notices."%user
            self._errors['user'] = ErrorList([msg])            
        
        return cleaned_data
    
