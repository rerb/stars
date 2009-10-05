import re

from django.forms import ModelForm
from django import forms
from django.forms import widgets
from django.forms.extras import widgets as extra_widgets 
from django.forms.util import ErrorList
from django.utils.safestring import mark_safe

from stars.apps.credits.models import *
from stars.apps.submissions.models import CreditTestSubmission
from stars.apps.dashboard.submissions.forms import CreditSubmissionForm
from stars.apps.helpers.forms import widgets as custom_widgets

class CreditSetForm(ModelForm):
    # version = forms.CharField(widget=widgets.TextInput(attrs={'size': 5})) # redundant?
    release_date = forms.DateField(widget=extra_widgets.SelectDateWidget())
        
    class Meta:
        model = CreditSet
        
#    @staticmethod
    def form_name():
        return u"Credit Set Form" 
    form_name = staticmethod(form_name)

class CategoryForm(ModelForm):
    
    class Meta:
        model = Category
        exclude = ('creditset', 'ordinal', 'max_point_value')
        
#    @staticmethod
    def form_name():
        return u"Category Form" 
    form_name = staticmethod(form_name)

class CategoryOrderForm(ModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(attrs={'class': 'ordinal',}))
    
    class Meta:
        model = Category
        fields = ('ordinal',)

#    @staticmethod
    def form_name():
        return u"Category Order Form" 
    form_name = staticmethod(form_name)
        
class SubcategoryForm(ModelForm):
    
    class Meta:
        model = Subcategory
        exclude = ('ordinal', 'max_point_value')
        
    def __init__(self, *args, **kwargs):
        """ Only allow categories from the same creditset """
        super(SubcategoryForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = [(cat.id, cat.title) for cat in self.instance.category.creditset.category_set.all()]

#    @staticmethod
    def form_name():
        return u"Subcategory Form" 
    form_name = staticmethod(form_name)

class NewSubcategoryForm(ModelForm):
    
    class Meta:
        model = Subcategory
        exclude = ('ordinal', 'max_point_value', 'category')
        
#    @staticmethod
    def form_name():
        return u"New Subcategory Form" 
    form_name = staticmethod(form_name)

class SubcategoryOrderForm(ModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(attrs={'class': 'ordinal',}))
    
    class Meta:
        model = Subcategory
        fields = ('ordinal',)
        
#    @staticmethod
    def form_name():
        return u"Subcategory Order Form" 
    form_name = staticmethod(form_name)

class CreditForm(ModelForm):
    title = forms.CharField(widget=widgets.TextInput(attrs={'size':'32'}))
    point_value = forms.CharField(widget=widgets.TextInput(attrs={'size':'3'}))
    
    class Meta:
        model = Credit
        exclude = ('ordinal', 'formula', 'number')

#    @staticmethod
    def form_name():
        return u"Credit Form" 
    form_name = staticmethod(form_name)

class CreditFormulaForm(ModelForm):
    formula = forms.CharField(widget=widgets.Textarea(attrs={'class': 'noMCE','rows': '16'}), required=True)

    class Meta:
        model = Credit
        fields = ('formula',)

#    @staticmethod
    def form_name():
        return u"Credit Formula Form" 
    form_name = staticmethod(form_name)

    def clean_formula(self):
        formula = self.cleaned_data['formula']
        # remove any funky (Mac and MS) newlines and replace tabs with spaces
        formula = formula.replace("\r\n", "\n")
        formula = formula.replace("\t", "    ")
        (success, message) = compile_formula(formula)
        if not success:
            raise forms.ValidationError(message)
        return formula
        
class CreditTestSubmissionForm(CreditSubmissionForm):
      
    class Meta:
        model = CreditTestSubmission
        fields = ['expected_value']
 
#    @staticmethod
    def form_name():
        return u"Formula Test Case Form" 
    form_name = staticmethod(form_name)

class NewCreditForm(CreditForm):
    
    class Meta(CreditForm.Meta):
        exclude = ('subcategory', 'ordinal', 'formula', 'number')

#    @staticmethod
    def form_name():
        return u"New Credit Form" 
    form_name = staticmethod(form_name)

class CreditOrderForm(ModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(attrs={'class': 'ordinal',}))
    
    class Meta:
        model = Credit
        fields = ('ordinal',)
        
#    @staticmethod
    def form_name():
        return u"Credit Order Form" 
    form_name = staticmethod(form_name)

class DocumentationFieldForm(ModelForm):
    tooltip_help_text = forms.CharField(widget=widgets.Textarea(attrs={'rows': '2'}), required=False)
    inline_help_text = forms.CharField(widget=widgets.Textarea(attrs={'rows': '4'}), required=False)
    
    class Meta:
        model = DocumentationField
        exclude = ('credit', 'ordinal', 'identifier')
        
#    @staticmethod
    def form_name():
        return u"Documentation Field Form" 
    form_name = staticmethod(form_name)

    def clean(self):
        cleaned_data = self.cleaned_data
        sel_type = cleaned_data.get("selection_type")
        type = cleaned_data.get("type")
        choices = cleaned_data.get('choices')
        
        if sel_type != 'user_defined':
            
            msg = ""
            if type != 'numeric' and type != 'text':
                msg = u"Choice options are only available for numeric and text fields."
            if type == 'numeric' and sel_type != 'choose_one':
                msg = u"\'Choose with Other\' and \'Choose Many\' selectors are only available for text fields."
            if msg:
                self._errors["selection_type"] = ErrorList([msg])
                del cleaned_data["selection_type"]
                
#            if choices:
#                msg = None
                # remove any funky newlines
#                if choices.count('\r\n'): # MS DOS
#                    choices = choices.replace('\r\n', '\n')
#                elif choices.count('\r'): # Mac
#                    choices = choices.replace('\r', '\n')
#                choices = choices.rstrip()
                
#                if type == 'numeric':
#                    choice_list = re.split('\n+', choices)
#                    for choice in choice_list:
#                        m = re.match('\d+\.?\d*', choice)
#                        if not m:
#                            msg = u"Please use valid numeric values"
#                            self._errors["choices"] = ErrorList([msg])
#                if not msg:
#                    cleaned_data['choices'] = choices
#            else:
#                msg = u"Please provide choices or set this documentation field to 'user-defined'."
#                self._errors["choices"] = ErrorList([msg])

        return cleaned_data
        
class DocumentationFieldOrderingForm(ModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(attrs={'size': '3', 'class': 'ordinal',}))
    
    class Meta:
        model = DocumentationField
        fields = ('ordinal',)
        
#    @staticmethod
    def form_name():
        return u"Documentation Field Ordering Form" 
    form_name = staticmethod(form_name)


class ChoiceForm(ModelForm):        
    class Meta:
        model = Choice
        fields = ('choice',)
        
#    @staticmethod
    def form_name():
        return u"Choice Form" 
    form_name = staticmethod(form_name)

class ChoiceOrderingForm(ModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(attrs={'size': '3', 'class': 'ordinal',}))
    
    class Meta:
        model = Choice
        fields = ('ordinal',)
        
#    @staticmethod
    def form_name():
        return u"Choices Ordering Form" 
    form_name = staticmethod(form_name)


class ApplicabilityReasonForm(ModelForm):
    
    class Meta:
        model = ApplicabilityReason
        exclude = ('credit')
        
#    @staticmethod
    def form_name():
        return u"Applicability Reason Form" 
    form_name = staticmethod(form_name)

class ConfirmDelete(forms.Form):
    confirm = forms.BooleanField()
