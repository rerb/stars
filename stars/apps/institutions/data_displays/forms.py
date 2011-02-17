from django import forms

TYPE_CHOICES = (
                    ("", "-------"),
                    ('org_type', 'Organization Type'),
                    ('rating', 'STARS Rating'),
                )
EMPTY_CHOICES = (
                    ("", "-------"),
                )

class AggregateFilterForm(forms.Form):
    
    type = forms.CharField(required=False, widget=forms.widgets.Select(choices=TYPE_CHOICES, attrs={'onchange': 'applyLookup(this);',}))
    item = forms.CharField(required=False, widget=forms.widgets.Select(choices=EMPTY_CHOICES))
    
    def clean(self):
        """
            This form can be empty, but if one is filled out then both must be
        """
        cleaned_data = self.cleaned_data
        type = cleaned_data.get("type")
        item = cleaned_data.get("item")

        if type and not item:
            self._errors["item"] = self.error_class([u"This field is required"])
            del cleaned_data["item"]

        return cleaned_data
        
    
class DelAggregateFilterForm(forms.Form):
    
    delete = forms.BooleanField(required=False, widget=forms.HiddenInput)
    
    def __init__(self, instance, *args, **kwargs):
        
        self.instance = instance
        return super(DelAggregateFilterForm, self).__init__(*args, **kwargs)