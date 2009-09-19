import sys
import string
from django.forms import ModelForm
from django import forms
from django.forms import widgets
from django.forms.extras.widgets import SelectDateWidget
from django.forms.util import ErrorList

from stars.apps.helpers.forms import widgets as custom_widgets
from stars.apps.helpers.decorators import render_with_units
from stars.apps.helpers import watchdog 
from stars.apps.submissions.models import *

class SubmissionFieldForm(ModelForm):
    """ Parent class for all submission fields to provide access to clean_value """

#    def clean_value(self):
#        """ Ensures that value is set if the submission is marked as complete """
#        value = self.cleaned_data.get("value")
#        if self.instance.credit_submission.is_complete() and not value:
#            raise forms.ValidationError("This field is required to mark this credit complete.")
#        return value

#    @staticmethod
    def form_name():
        return u"Credit Submission Form" 
    form_name = staticmethod(form_name)

#    @staticmethod
    def get_form_class(submission_field):
        """Return the class for the Form matching the submission_field"""
        SubmissionFormsModule = sys.modules[__name__]
        FormClass = getattr(SubmissionFormsModule, "%sForm"%submission_field.__class__.__name__ , None)
        return FormClass
    get_form_class = staticmethod(get_form_class)
    
    def _has_multi_widget(self):
        """ Return True iff this field has an instance that specifies a multi-valued widget """
        return self.instance and \
               self.instance.documentation_field.has_multiple_values()
               
    def _add_widget_options(self):
        """ 
            Add any specified options to the submission field widget, including:
                - choice options (changes the default widget type)
                - units (adds units to the widget display)
        """
        CHOICE_WIDGETS = {
                      'choose_one': widgets.Select,
                      'choose_many': widgets.CheckboxSelectMultiple,
                      'choose_one_other': custom_widgets.SelectWithOtherWidget,
                      'choose_many_other': custom_widgets.CheckboxSelectMultipleWithOtherWidget,
        }
        if self.instance:
            doc_field = self.instance.documentation_field
            type = doc_field.selection_type
            if doc_field.choices :
                choices = doc_field.get_choices()
                if type in CHOICE_WIDGETS.keys():
                    self.fields['value'].widget = CHOICE_WIDGETS[type](choices=choices)
            if doc_field.units:
                widget = self.fields['value'].widget
                # special case to display units with "other" for choice_with_other type widgets...
                if doc_field.has_other_choice():
                    widget.set_units(doc_field.units)
                elif not doc_field.includes_units():  # for fields that don't include their units, render the units after the field
                    widget.render = render_with_units(widget.render, doc_field.units)
                # else the field includes units and will render them as part of the widget.
                
    def _compress(self, value):
        """ 
            Value from multi-valued choice widgets (with_other) need to be compressed into a single value
            Compress should really be part of a multi-value field - but our fields are fixed-type
            Returns the compressed value or simply value if no need to compress
        """
        if not self._has_multi_widget():
            return value
        # assert: this field has an instance that used a multi-valued widget to collect the data.
        print "Multi-value form cleaned_data = %s"%value
        #### MOVE THIS LOGIC TO THE WIDGET CLASS?  Seems smart - match with decompress?
        #### Avoids select - just call widget.compress.  Need to subclass CheckboxSelectMultiple to add compress / decompress?
        #### Maybe we should have another field type to store multi-valued fields as a list?
        type = self.instance.documentation_field.selection_type 
        choices = self.instance.documentation_field.get_choices()
        # assert value is a list and len(value) == 2  # in  python?
        if type == 'choose_one_other':
            # if the last choice was selected, then the user specified the 'other' value...
            # index = value[0].to_numeric()  # ????
            #if index == len(choices)-1:  # use the 'other' value
            #    result = value[1]
            #else:  # use the choice selected
            #    result = choices[index]
            result = value
        elif type == 'choose_many':
            result = value
        elif type == 'choose_many_other':
            result = value
        else:
            result = value  # @todo: this indicates a logic inconsistency - log an error or raise an exception? 
        print "Compressed to: %s"%result
        return result
    
class URLSubmissionForm(SubmissionFieldForm):
    class Meta:
        model = URLSubmission
        fields = ['value']
    
class DateSubmissionForm(SubmissionFieldForm):
    value = forms.DateField(widget=SelectDateWidget(required=False), required=False)
    
    def __init__(self, *args, **kwargs):
        """ If there is an instance, use the date range from that instance. """
        super(DateSubmissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            min = self.instance.documentation_field.min_range
            max = self.instance.documentation_field.max_range
            if min != None and max != None:
                self.fields['value'].widget = SelectDateWidget(required=False, years=range(min, max))
    
    class Meta:
        model = DateSubmission
        fields = ['value']
    
class NumericSubmissionForm(SubmissionFieldForm):
    class Meta:
        model = NumericSubmission
        fields = ['value']
    
    def __init__(self, *args, **kwargs):
        """ If there is an instance with choices, set up the choices. """
        super(NumericSubmissionForm, self).__init__(*args, **kwargs)
        self._add_widget_options()
        
    def clean_value(self):
        """ If there is a range, use this to validate the number """
        value = self.cleaned_data.get("value")
        if self.instance:
            min = self.instance.documentation_field.min_range
            max = self.instance.documentation_field.max_range
            
            if min != None and max != None:
                if value < min or value > max:
                    raise forms.ValidationError("Valid Range: %d - %d" % (min, max))
        else:
            watchdog.log("NumericSubmission", "No Instance", watchdog.NOTICE) 
        return value
    
class TextSubmissionForm(SubmissionFieldForm):
    class Meta:
        model = TextSubmission
        fields = ['value']
    
    def __init__(self, *args, **kwargs):
        """ If there is an instance with choices, set up the choices. """
        super(TextSubmissionForm, self).__init__(*args, **kwargs)
        self._add_widget_options()
        if self.instance:
            max = self.instance.documentation_field.max_range
            if max != None:
                self['value'].field.widget.attrs['maxlength'] = max
    
    def clean_value(self):
        """ Compress multi-valued data and validate ranges (character or word counts) """
#        value = self._compress(self.cleaned_data.get("value"))
        value = self.cleaned_data.get("value")
        if self.instance:
            max = self.instance.documentation_field.max_range

            chars = len(value)
            
            if max != None:
                if chars > max:
                    raise forms.ValidationError("Too long. Limit: %d characters"% max)
        else:
            watchdog.log("TextSubmission", "No Instance", watchdog.NOTICE)
        return value
    
class LongTextSubmissionForm(SubmissionFieldForm):
    value = forms.CharField(widget=widgets.Textarea(attrs={'class': 'noMCE'}), required=False)  # don't use MCE for submissions!

    class Meta:
        model = LongTextSubmission
        fields = ['value']
        
    def clean_value(self):
        """ If there is a range, use this to validate the character count """
        value = self.cleaned_data.get("value")
        if self.instance:
            max = self.instance.documentation_field.max_range

            words = len(string.split(value))
            
            if max != None:
                if words > max:
                    raise forms.ValidationError("Too many words. Limit: %d" % max)
        else:
            watchdog.log("LongTextSubmission", "No Instance", watchdog.NOTICE)
        return value
    
class UploadSubmissionForm(ModelForm):
    """
        The submitted value for a File Upload Documentation Field
    """
    #value = models.FileField()  @TODO file handling
    
class BooleanSubmissionForm(SubmissionFieldForm):
    class Meta:
        model = BooleanSubmission
        fields = ['value']


class CreditSubmissionForm(ModelForm):
    """
        A collection of SubmissionFieldForms along with methods to process them.
        This class is primarily here to serve as a base class for User and Test submission forms.
        Warning: Currently, rendering the form using as_p or similar will only render
                 fields defined by the sub-class.  
                 Templates must include "dashboard/submissions/submission_fields_form.html" to render the submission field elements themselves.
    """
    class Meta:
        model = CreditSubmission
        fields = [] # This is an abstract base class - not to be used directly!

#    @staticmethod
    def form_name():
        return u"Credit Submission Form" 
    form_name = staticmethod(form_name)

    def __init__(self, *args, **kwargs): #data=None, instance=None, prefix='credit-submission'):
        """
            Construct a form to edit a CreditSubmission instance
            @param instance: CreditSubmission (or sub-class) object is REQUIRED
        """
        if not kwargs.has_key('instance') or not kwargs['instance']:
            raise Exception('CreditSubmission object is required for CreditSubmissionform')
        super(CreditSubmissionForm, self).__init__(*args, **kwargs)

        self._form_fields = None        # lazy init - don't access directly, call get_from_fields()

    def get_submission_fields_and_forms(self):
        """ 
            Get a list of submission field form elements for this Form;
            @return: submission_field_list: list of fields and form elements
                Each item in the submission_field_list is a dictionary with elements 'field' and 'form'
        """
        if self._form_fields:  # lazy init
            return self._form_fields
        # else... do the work... 
        self._form_fields = []

        # CAUTION: ModelForm stores any POST data during form construction,
        #       BUT, if there was no POST data, the Form stores data={}.  
        #       Thus, when we populate the Submission Field forms below from their associated instances, 
        #          we need to be careful that the forms receive data=None instead of data={}, otherwise the Form binds the field to the empty dict rather than the instance!!!
        if self.is_bound:
            data = self.data
        else:
            data = None

        # build the form fields based on the data and instance bound to this form.
        prefix = 0  # Ideally, form prefix would be submission field id, but this may not be set yet, and each must be unique.
        for field in self.instance.get_submission_fields():
            prefix +=1
            SubmissionFieldFormClass = SubmissionFieldForm.get_form_class(field)
            if SubmissionFieldFormClass:
                # bind the field form to the data (if there was any)
                form = SubmissionFieldFormClass(data, instance=field, prefix="%s_%s"%(field.__class__.__name__,prefix) )
                self._form_fields.append({'field': field, 'form': form})
                
        return self._form_fields
    
    def save(self, commit=True):
        """ 
            Save the data in this form (update instance or create a new submission) 
            @return: the updated CreditSubmission instance.
        """
        # This is a bit tricky:
        #    CreditSubmission object needs the new form field values to calculate points,
        #    but the form fields need the CS objet to be saved so they can store a foreign key to it...
        for field in self.get_submission_fields_and_forms():
            field['field'] = field['form'].save(False)

        self.instance = super(CreditSubmissionForm, self).save(commit)

        for field in self.get_submission_fields_and_forms():
            # Ensure field form has the newly saved instance of the CreditSubmission object
            field['form'].instance.credit_submission = self.instance
            field['form'].save(commit)
            
        return self.instance

    
    def is_valid(self):
        """ Perform data validation on the form and return True if it all passes """
        is_valid = True
        
        # Caution: validation order is, unfortunately, important here...
        #  the Submission Fields are validated fist, so their cleaned_data
        #  is available when we validate, and thus clean(), the Form itself.
        for field in self.get_submission_fields_and_forms():
            if not field['form'].is_valid():
                is_valid = False 
        
        # use short-cut evaluation here so Form is not validated if fields don't validate.
        return is_valid and super(CreditSubmissionForm, self).is_valid()
    

class CreditUserSubmissionForm(CreditSubmissionForm):
    """
        A Credit Submission Form for a user submission, with Submission Status
    """
    submission_status = forms.CharField(widget=forms.RadioSelect(choices=CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED))
    applicability_reason = forms.ModelChoiceField(queryset=None, empty_label=None, widget=forms.RadioSelect(), required=False)

    class Meta:
        model = CreditUserSubmission
        fields = ['submission_status', 'applicability_reason']

    def __init__(self, *args, **kwargs):
        super(CreditUserSubmissionForm, self).__init__(*args, **kwargs)
        # if there are reasons that this might not apply, allow the "not applicable" choice
        if self.instance.credit.applicabilityreason_set.all():
            self.fields['applicability_reason'].queryset=self.instance.credit.applicabilityreason_set.all()
            self.fields['submission_status'].widget = forms.RadioSelect(choices=CREDIT_SUBMISSION_STATUS_CHOICES_W_NA, attrs={'onchange': 'toggle_applicability_reasons(this)'})

    def clean(self):
        """
            Submission status depends on status of required fields - can't submit as complete when its not!
            An applicability reason must be selected if the submission status is set to 'na'
            Otherwise we want the reason to be None
        """
        cleaned_data = self.cleaned_data
        status = cleaned_data.get("submission_status")
        reason = cleaned_data.get("applicability_reason")

        if not status :
            msg = u"Please tick the appropriate status for this submission."
            self._errors["submission_status"] = ErrorList([msg])
        if status == 'na' and not reason:
            msg = u"Please select a reason why this does not apply."
            self._errors["applicability_reason"] = ErrorList([msg])
        if not status == 'na':
            cleaned_data["applicability_reason"] = None
        
        # Check that status was not marked complete when required fields are missing
        marked_complete = (status=='c')
        error = False
        for field in self.get_submission_fields_and_forms():
            value = field['form'].cleaned_data.get("value")
            if field['field'].documentation_field.is_required and \
               marked_complete and (value==None or value==""):
                msg = u"This field is required to mark this credit complete."
                field['form']._errors["value"] = ErrorList([msg])
                error = True
        if (error):
            raise forms.ValidationError("This credit cannot be submitted as complete.")
            
        return cleaned_data