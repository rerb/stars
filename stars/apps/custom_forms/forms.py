from django.forms import ModelForm

from stars.apps.custom_forms.models import TAApplication
from stars.apps.credits.models import Subcategory

class TAApplicationForm(ModelForm):
    
    class Meta:
        model = TAApplication
        # ordering
        fields = ["first_name", "last_name", "title", "department", "institution", "phone_number", "email", "address", "city", "state", "zipcode", "instituion_type", "subcategories", "skills_and_experience", "related_associations", "resume", "credit_weakness"]
        
    def __init__(self, *args, **kwargs):
        
        super(TAApplicationForm, self).__init__(*args, **kwargs)
        
        self.fields['skills_and_experience'].label = "Describe what skills and experience you'd bring to the position"
        self.fields['related_associations'].label = "List any related associations, committees, or organizations in which you are a member"
        self.fields['resume'].label = "Upload a copy of your resume or CV"
        self.fields['credit_weakness'].label = "Briefly describe a weakness of a STARS credit or subcategory, including how it could be improved"
        self.fields['subcategories'].label = "Select the STARS sub-categories for which you wish to serve as a Technical Advisor"
        
        subset = Subcategory.objects.exclude(title='Demo').exclude(title='Innovation')
        self.fields['subcategories'].choices = [(s.id, s.title) for s in subset]