import sys
import string
from django.forms import ModelForm
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms.util import ErrorList
from django.contrib.admin.widgets import AdminFileWidget

from stars.apps.helpers.forms import fields as custom_fields
from stars.apps.helpers.decorators import render_with_units
from stars.apps.helpers import watchdog 
from stars.apps.submissions.models import *

class SubmissionFieldForm(ModelForm):
    """ Parent class for all submission fields to provide access to clean_value """
    def __init__(self, *args, **kwargs):
        """ Add any specified options to the form's value field """
        super(SubmissionFieldForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.get_units():
            if self.field_includes_units():
                self.fields['value'].set_units(self.instance.get_units())
            else:  # for fields that don't include their units, render the units after the field
                widget = self.fields['value'].widget
                widget.render = render_with_units(widget.render, self.instance.get_units())

    def field_includes_units(self):
        """ Returns true if the form field contains its own units, false otherwise """
        return self.__class__ in (ChoiceWithOtherSubmissionForm, MultiChoiceSubmissionForm, MultiChoiceWithOtherSubmissionForm)

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
        """Return the class for the Form matching the DocumentationFieldSubmission submission_field model"""
        SubmissionFormsModule = sys.modules[__name__]
        FormClass = getattr(SubmissionFormsModule, "%sForm"%submission_field.__class__.__name__ , None)
        return FormClass
    get_form_class = staticmethod(get_form_class)
    
class AbstractChoiceSubmissionForm(SubmissionFieldForm):
    """ An abstract base class to provide some of the baseline behaviour for choice-type field forms. """
    class Meta:
        abstract = True
        
    def __init__(self, *args, **kwargs):
        """ 
            Set up the choice's for the 'value' field on the form:
             - choices are drawn from the bonafide Choices defined for its doc. field.
            Note: widget cannot be replaced after this call!!  Currently, subclasses must use value field's default widget...
        """
        super(AbstractChoiceSubmissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['value'].queryset = self.instance.get_choice_queryset()

class AbstractMultiFieldSubmissionForm(AbstractChoiceSubmissionForm):
    """ An abstract base class for choice-with-other-type and other multi-field submissionforms. """
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """  Hook up the compress / decompress logic for the multi-field """
        super(AbstractMultiFieldSubmissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['value'].set_compress_methods(self.instance.compress, self.instance.decompress)
        
class ChoiceSubmissionForm(AbstractChoiceSubmissionForm):
    # Uses the defaut ChoiceField and widget.
    class Meta:
        model = ChoiceSubmission
        fields = ['value']

 
class ChoiceWithOtherSubmissionForm(AbstractMultiFieldSubmissionForm):
    value = custom_fields.ModelChoiceWithOtherField(required=False)
    
    class Meta:
        model = ChoiceSubmission
        fields = ['value']


class MultiChoiceSubmissionForm(AbstractChoiceSubmissionForm):    
    value = custom_fields.ModelMultipleChoiceCheckboxField(required=False)

    class Meta:
        model = MultiChoiceSubmission
        fields = ['value']


class MultiChoiceWithOtherSubmissionForm(AbstractMultiFieldSubmissionForm):
    value = custom_fields.ModelMultipleChoiceWithOtherField(required=False)
    
    class Meta:
        model = MultiChoiceSubmission
        fields = ['value']

  
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
        if self.instance:
            max = self.instance.documentation_field.max_range
            if max != None:
                self['value'].field.widget.attrs['maxlength'] = max
    
    def clean_value(self):
        """ Compress multi-valued data and validate ranges (character or word counts) """
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
    value = forms.CharField(widget=forms.Textarea(attrs={'class': 'noMCE'}), required=False)  # don't use MCE for submissions!

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
    class Meta:
        model = UploadSubmission
        fields = ['value']
        
    def __init__(self, *args, **kwargs):
        """ Change the widget """
        super(UploadSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget = AdminFileWidget()
    
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
            files = self.files
        else:
            data = None
            files = None
            
        # build the form fields based on the data and instance bound to this form.
        prefix = 0  # Ideally, form prefix would be submission field id, but this may not be set yet, and each must be unique.
        for field in self.instance.get_submission_fields():
            prefix +=1
            SubmissionFieldFormClass = SubmissionFieldForm.get_form_class(field)
            if SubmissionFieldFormClass:
                # bind the field form to the data (if there was any)
                form = SubmissionFieldFormClass(data, files, instance=field, prefix="%s_%s"%(field.__class__.__name__,prefix) )
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
    
class ResponsiblePartyForm(ModelForm):
    """
        When adding a new Responsible Party
    """
    
    class Meta:
        model = ResponsibleParty
        exclude = ['institution',]

class CreditUserSubmissionForm(CreditSubmissionForm):
    """
        A Credit Submission Form for a user submission, with Submission Status
    """
    submission_status = forms.CharField(widget=forms.RadioSelect(choices=CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED))
    applicability_reason = forms.ModelChoiceField(queryset=None, empty_label=None, widget=forms.RadioSelect(), required=False)

    class Meta:
        model = CreditUserSubmission
        fields = ['internal_notes', 'submission_notes', 'responsible_party_confirm', 'responsible_party', 'submission_status', 'applicability_reason']

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
               marked_complete and value in (None, "", []):
                msg = u"This field is required to mark this credit complete."
                field['form']._errors["value"] = ErrorList([msg])
                error = True
            
        # responsible party and responsible party confirm are required if marked complete
        if marked_complete:
            rp = cleaned_data.get("responsible_party")
            if rp == None or rp == "":
                msg = u"This field is required to mark this credit complete."
                self._errors["responsible_party"] = ErrorList([msg])
                error = True
            rpc = cleaned_data.get("responsible_party_confirm")
            if not rpc:
                msg = u"This field is required to mark this credit complete."
                self._errors["responsible_party_confirm"] = ErrorList([msg])
                error = True
                
        if (error):
            raise forms.ValidationError("This credit cannot be submitted as complete.")
    
        return cleaned_data