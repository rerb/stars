from django import forms
from django.utils.safestring import mark_safe

import string, re

from stars.apps.credits.models import CreditSet, Category, Subcategory, Credit, DocumentationField

TYPE_CHOICES = (
                    ("", "-------"),
                    ('org_type', 'Organization Type'),
                    ('rating__name', 'STARS Rating'),
                )
EMPTY_CHOICES = (
                    ("", "-------"),
                )

class CharacteristicFilterForm(forms.Form):
    
    type = forms.CharField(required=False, widget=forms.widgets.Select(choices=EMPTY_CHOICES))
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
    
    def __init__(self, available_filters, **kwargs):
        
        super(CharacteristicFilterForm, self).__init__(**kwargs)
        
        choices = [("", "-------")]
        for f in available_filters:
            choices.append((f.key, f.title))
            
        self.fields['type'].widget = forms.widgets.Select(choices=choices, attrs={'onchange': 'applyLookup(this);',})
    
class DelCharacteristicFilterForm(forms.Form):
    
    delete = forms.BooleanField(required=False, widget=forms.HiddenInput)
    
    def __init__(self, instance, *args, **kwargs):
        
        self.instance = instance
        super(DelCharacteristicFilterForm, self).__init__(*args, **kwargs)
    

class CreditSetElementField(forms.CharField):
    
    def to_python(self, value):
        "Normalize data to a Category, Subcategory, or Credit."

        # Return an empty list if no input was given.
        if value and value != 'select_one':
            pattern = "(\w+)_(\d+)"
            m = re.match(pattern, value)
            if m:
                obj = m.groups()[0]
                id = m.groups()[1]
                if obj == "cat":
                    return Category.objects.get(pk=id)
                if obj == "sub":
                    return Subcategory.objects.get(pk=id)
                if obj == "cred":
                    return Credit.objects.get(pk=id)
        return None

class ScoreColumnForm(forms.Form):
    
    column_1 = CreditSetElementField(required=False)
    column_2 = CreditSetElementField(required=False)
    column_3 = CreditSetElementField(required=False)
    column_4 = CreditSetElementField(required=False)
    
    def __init__(self, *args, **kwargs):
        
#        self.instance = instance
        
        if kwargs.has_key('initial'):
            initial = kwargs['initial']
            new_initial = {}
            count = 0
            if initial:
                for k, col in initial.items():
                    if isinstance(col, Category):
                        new_initial[k] = "cat_%d" % col.id
                    elif isinstance(col, Subcategory):
                        new_initial[k] = "sub_%d" % col.id
                    elif isinstance(col, Credit):
                        new_initial[k] = "cred_%d" % col.id
                    else:
                        new_initial[k] = "select_one"
                    count += 1
            else:
                for i in range(1,5):
                    new_initial['column_%d' % i] = "select_one"
            
            kwargs['initial'] = new_initial
        
        super(ScoreColumnForm, self).__init__(*args, **kwargs)
        
        choices = [("select_one", "Select One")]
        disabled = []
        
        for cat in CreditSet.objects.get(pk=2).category_set.all():
            choices.append(("cat_%d" % cat.id, string.upper(cat.title)))
#            spacer = ("cat_%d_spacer" % cat.id, "")
            choices.append(('', ''))
#            disabled.append(spacer)
            
            for sub in cat.subcategory_set.all():
                choices.append(("sub_%d" % sub.id, mark_safe("&nbsp;%s" % sub.title)))
#                spacer = ("sub_%d_spacer" % sub.id, "")
#                choices.append(spacer)
#                disabled.append(spacer)
                choices.append(('', ''))
                
                for c in sub.get_tier1_credits():
                    choices.append(("cred_%d" % c.id, mark_safe("&nbsp;&nbsp;&nbsp;%s" % c.title)))
                    
                t2 = sub.get_tier2_credits()
                if t2:
#                    spacer = ("sub_%d_t2spacer" % sub.id, mark_safe("&nbsp;&nbsp;&nbsp;-------"))
                    choices.append(('', mark_safe('&nbsp;&nbsp;&nbsp;-------')))
#                    choices.append(spacer)
#                    disabled.append(spacer)
                    for c in t2:
                        choices.append(("cred_%d" % c.id, mark_safe("&nbsp;&nbsp;&nbsp;%s" % c.title)))
                
#                spacer = ("sub_%d_spacer2" % sub.id, "")
#                choices.append(spacer)
#                disabled.append(spacer)
                choices.append(('', ''))
                
        w = forms.Select(choices=choices)
        
        self.fields['column_1'].widget = w
        self.fields['column_2'].widget = w
        self.fields['column_3'].widget = w
        self.fields['column_4'].widget = w
    
class ReportingFieldSelectForm(forms.Form):
    
    reporting_field = forms.ModelChoiceField(DocumentationField, required=False)
    
    def __init__(self, *args, **kwargs):
        
        super(ReportingFieldSelectForm, self).__init__(*args, **kwargs)
               
        cs = CreditSet.objects.get(pk=2)
        cs_lookup = "credit__subcategory__category__creditset"
        self.fields['reporting_field'].queryset = DocumentationField.objects.filter(**{cs_lookup: cs}) 
        
        self.fields['reporting_field'].widget.choices = (('', '--------'),)
        
    def clean(self):
        
        cleaned_data = self.cleaned_data
        
        return cleaned_data
