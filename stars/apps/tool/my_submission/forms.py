from logging import getLogger
import sys
import string

from django.forms import ModelForm, widgets
from django.forms.widgets import TextInput, ClearableFileInput, HiddenInput
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms.util import ErrorList
from django.utils.safestring import mark_safe

from stars.apps.helpers.forms import fields as custom_fields
from stars.apps.helpers.forms.forms import LocalizedModelFormMixin
from stars.apps.helpers.forms.util import WarningList
from stars.apps.submissions.models import *

from form_utils.forms import BetterModelForm

logger = getLogger('stars')


class NewBoundaryForm(LocalizedModelFormMixin, BetterModelForm):

    class Meta:
        model = Boundary
        exclude = ("submissionset",)

        fieldsets = [ ('Characteristics',
                       { 'fields':Boundary.get_characteristic_field_names(),
                         'legend': "Characteristics",
                         'description': 'boundary_characteristics' }),
                      ('Features',
                       { 'fields': [ 'ag_school_present',
                                     'ag_school_included',
                                     'ag_school_details',
                                     'med_school_present',
                                     'med_school_included',
                                     'med_school_details',
                                     'pharm_school_present',
                                     'pharm_school_included',
                                     'pharm_school_details',
                                     'pub_health_school_present',
                                     'pub_health_school_included',
                                     'pub_health_school_details',
                                     'vet_school_present',
                                     'vet_school_included',
                                     'vet_school_details',
                                     'sat_campus_present',
                                     'sat_campus_included',
                                     'sat_campus_details',
                                     'hospital_present',
                                     'hospital_included',
                                     'hospital_details',
                                     'farm_present',
                                     'farm_included',
                                     'farm_acres',
                                     'farm_details',
                                     'agr_exp_present',
                                     'agr_exp_included',
                                     'agr_exp_acres',
                                     'agr_exp_details' ],
                         'legend': 'Features',
                         'description': 'boundary_features' }),
                      ('narrative',
                       { 'fields': ['additional_details'],
                         'legend': "Narrative",
                         "description": "boundary_narrative" }) ]

    def __init__(self, *args, **kwargs):
        super(NewBoundaryForm, self).__init__(*args, **kwargs)


class SubcategorySubmissionForm(ModelForm):

    class Meta:
        model = SubcategorySubmission
        fields = ('description',)

    def __init__(self, *args, **kwargs):
        super(SubcategorySubmissionForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget.attrs = {
            'onkeydown': 'field_changed(this);',
            'onchange': 'field_changed(this);',
            'style': 'width: 35em;height: 15em;' }


class SubmissionFieldFormMixin():

    def append_error(self, msg):
        """ Helper to append or add new error message to this form's
        value field error list"""
        if "value" in self._errors:
            self._errors["value"].append(msg)
        else:
            self._errors["value"] = ErrorList([msg])

    def append_warning(self, msg):
        """ Helper to append or add new warning message to this form's
        value field warning list"""
        if self.warnings:
            self.warnings.append(msg)
        else:
            self.warnings = WarningList([msg])


class SubmissionFieldForm(SubmissionFieldFormMixin, LocalizedModelFormMixin, ModelForm):
    """ Parent class for all submission fields to provide access to
    clean_value"""

    def __init__(self, *args, **kwargs):
        """ Add any specified options to the form's value field """
        super(SubmissionFieldForm, self).__init__(*args, **kwargs)
        self.warnings = None

    def field_includes_units(self):
        """ Returns true if the form field contains its own units,
        false otherwise"""
        return self.__class__ in (ChoiceWithOtherSubmissionForm,
                                  MultiChoiceSubmissionForm,
                                  MultiChoiceWithOtherSubmissionForm)

    def form_name():
        return u"Credit Submission Form"
    form_name = staticmethod(form_name)

    def get_form_class(submission_field):
        """Return the class for the Form matching the
        DocumentationFieldSubmission submission_field model"""
        SubmissionFormsModule = sys.modules[__name__]
        FormClass = getattr(SubmissionFormsModule,
                            "%sForm"%submission_field.__class__.__name__ , None)
        return FormClass
    get_form_class = staticmethod(get_form_class)


class AbstractChoiceSubmissionForm(SubmissionFieldForm):
    """ An abstract base class to provide some of the baseline
    behaviour for choice-type field forms."""
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """
            Set up the choice's for the 'value' field on the form:

            - choices are drawn from the bonafide Choices defined for
              its doc. field.

            Note: widget cannot be replaced after this call!!
            Currently, subclasses must use value field's default
            widget...
        """
        super(AbstractChoiceSubmissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['value'].queryset = self.instance.get_choice_queryset()


class AbstractMultiFieldSubmissionForm(AbstractChoiceSubmissionForm):
    """ An abstract base class for choice-with-other-type and other
    multi-field submissionforms."""
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """  Hook up the compress / decompress logic for the multi-field """
        super(AbstractMultiFieldSubmissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['value'].set_compress_methods(self.instance.compress,
                                                      self.instance.decompress)


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
    value = forms.URLField(required=False, verify_exists=False,
                           widget=TextInput(attrs={'style': 'width: 600px;',}))

    class Meta:
        model = URLSubmission
        fields = ['value']


class DateSubmissionForm(SubmissionFieldForm):
    value = forms.DateField(widget=SelectDateWidget(required=False),
                            required=False)

    def __init__(self, *args, **kwargs):
        """ If there is an instance, use the date range from that instance. """
        super(DateSubmissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            min = self.instance.documentation_field.min_range
            max = self.instance.documentation_field.max_range
            if min != None and max != None:
                self.fields['value'].widget = SelectDateWidget(
                    required=False, years=range(min, max+1))

    class Meta:
        model = DateSubmission
        fields = ['value']


class MetricWidget(widgets.TextInput):
    """A TextInput that converts its value into its Metric equivalent.

    The conversion happens in render(), so is visible to the user.

    Used by NumericSubmissionForm when the institution in question
    prefers the Metric system.
    """

    def __init__(self, units, *args, **kwargs):
        self.units = units
        super(MetricWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        """Convert `value` to metric equivalent quantity."""
        if value and self.units:
            value = float(value)  # sometimes value is a string  :-(
            value = self.units.convert(value)
        return super(MetricWidget, self).render(name, value, attrs)


class NumericSubmissionForm(SubmissionFieldForm):

    class Meta:
        model = NumericSubmission
        fields = ['value']

    def __init__(self, *args, **kwargs):
        super(NumericSubmissionForm, self).__init__(*args, **kwargs)

        institution = self.instance.get_institution()
        self.use_metric_system = institution.prefers_metric_system

        if self.use_metric_system:
            self.units = self.instance.documentation_field.metric_units
            self.fields['value'].widget = MetricWidget(units=self.units)

    def clean_value(self):
        """ If we're displaying a metric quantity, revert it to its
            US equivalent.

            If there is a range, use this to validate the number.
        """
        value = self.cleaned_data.get("value")

        if self.use_metric_system and value and self.units:
            value = self.units.revert(value)

        if self.instance and not (value is None):
            min = self.instance.documentation_field.min_range
            max = self.instance.documentation_field.max_range

            if (min is not None and
                max is not None and
                (value < min or
                 value > max)):
                self.raise_validation_error(
                    error_message=("The value is outside of the accepted "
                                   "range for this field (range: {min} - "
                                   "{max})."),
                    min=min,
                    max=max)
            elif (min is not None and
                  value < min):
                self.raise_validation_error(
                    error_message=("The value is must be greater than or "
                                   "equal to {min}."),
                    min=min)
            elif (max is not None and
                  value > max):
                self.raise_validation_error(
                    error_message=("The value is must be less than or equal "
                                   "to {max}"),
                    max=max)
        elif not self.instance:
            logger.info("No Instance")

        return value

    def raise_validation_error(self, error_message, min=None, max=None):
        """Raises forms.ValidationError, converting `min` and `max` in
        the error message to metric, when appropriate.
        """
        if self.use_metric_system and self.units:
            for num in min, max:
                if num:
                    num = self.units.convert(num)
        raise forms.ValidationError(error_message.format(min=min, max=max))


class TextSubmissionForm(SubmissionFieldForm):
    class Meta:
        model = TextSubmission
        fields = ['value']

    def __init__(self, *args, **kwargs):
        """ If there is an instance with choices, set up the choices. """
        super(TextSubmissionForm, self).__init__(*args, **kwargs)
        self['value'].field.widget.attrs['style'] = "width: 600px;"
        if self.instance:
            max = self.instance.documentation_field.max_range
            if max != None:
                self['value'].field.widget.attrs['maxlength'] = max

    def clean_value(self):
        """ Validate the character count """
        value = self.cleaned_data.get("value")
        if self.instance and value:
            max = self.instance.documentation_field.max_range

            chars = len(value)

            if max != None:
                if chars > max:
                    raise forms.ValidationError(
                        "The text is too long for this field. "
                        "Limit: %d characters"% max)
        elif not self.instance:
            logger.info("No Instance")
        return value


class LongTextSubmissionForm(SubmissionFieldForm):
    value = forms.CharField(
        widget=forms.Textarea(
            attrs={'style': 'width: 600px;height:100px;'}),
            required=False)  # don't use MCE for submissions!

    class Meta:
        model = LongTextSubmission
        fields = ['value']

    def clean_value(self):
        """ Validate the word count """
        value = self.cleaned_data.get("value")
        if self.instance and value:
            max = self.instance.documentation_field.max_range

            words = len(string.split(value))

            if max != None:
                if words > max:
                    raise forms.ValidationError(
                        "The text is too long for this field. "
                        "Limit: %d words" % max)
        elif not self.instance:
            logger.info("No Instance")
        return value


class UploadSubmissionForm(SubmissionFieldForm):
    """
        The submitted value for a File Upload Documentation Field
    """
    class Meta:
        model = UploadSubmission
        fields = ['value']

    def __init__(self, *args, **kwargs):
        """ Change the widget """
        super(UploadSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget = ClearableFileInput()

    def save(self, *args, **kwargs):
        instance = super(UploadSubmissionForm, self).save(*args, **kwargs)
        # Once the POST data has been saved, force form to be bound to
        # the saved instance.  See ticket #338
        self.files={}
        self.data={}
        from django.forms import model_to_dict
        self.initial.update(model_to_dict(instance))
        return instance


class BooleanSubmissionForm(SubmissionFieldForm):
    class Meta:
        model = BooleanSubmission
        fields = ['value']


class CreditSubmissionForm(LocalizedModelFormMixin, ModelForm):
    """
        A collection of SubmissionFieldForms along with methods to
        process them.  This class is primarily here to serve as a base
        class for User and Test submission forms.  Warning: Currently,
        rendering the form using as_p or similar will only render
        fields defined by the sub-class.  Templates must include
        "tool/submissions/submission_fields_form.html" to render the
        submission field elements themselves.
    """
    class Meta:
        model = CreditSubmission
        fields = [] # This is an abstract base class - not to be used directly!

    def __init__(self, *args, **kwargs):
        """
            Construct a form to edit a CreditSubmission instance
            @param instance: CreditSubmission (or sub-class) object is REQUIRED
        """
        if not kwargs.has_key('instance') or not kwargs['instance']:
            raise Exception('CreditSubmission object is required '
                            'for CreditSubmissionForm')
        super(CreditSubmissionForm, self).__init__(*args, **kwargs)

        self.warnings = None  # Top-level warnings for this form
                              #(filled by custom validation)
        self._form_fields = None  # lazy init - don't access directly,
                                  # call get_from_fields()

    def form_name():
        return u"Credit Submission Form"
    form_name = staticmethod(form_name)

    def get_submission_fields_and_forms(self):
        """
            Get a list of submission field form elements for this Form;

            @return: submission_field_list: list of fields and form elements

            Each item in the submission_field_list is a dictionary
            with elements 'field' and 'form'
        """
        if self._form_fields:  # lazy init
            return self._form_fields
        # else... do the work...
        self._form_fields = []

        # CAUTION: ModelForm stores any POST data during form
        # construction, BUT, if there was no POST data, the Form
        # stores data={}.  Thus, when we populate the Submission Field
        # forms below from their associated instances, we need to be
        # careful that the forms receive data=None instead of data={},
        # otherwise the Form binds the field to the empty dict rather
        # than the instance!!!
        if self.is_bound:
            data = self.data
            files = self.files
        else:
            data = None
            files = None

        # build the form fields based on the data and instance bound
        # to this form.
        prefix = 0  # Ideally, form prefix would be submission field
                    #id, but this may not be set yet, and each must be
                    #unique.

        for field in self.instance.get_submission_fields():
            prefix +=1
            SubmissionFieldFormClass = SubmissionFieldForm.get_form_class(field)
            if SubmissionFieldFormClass:
                # bind the field form to the data (if there was any)
                form = SubmissionFieldFormClass(
                    data, files, instance=field,
                    prefix="%s_%s"%(field.__class__.__name__,prefix))
                form['value'].field.widget.attrs['onchange'] = (
                    'field_changed(this);')  # see include.js
            else:
                ## Dummy Tabular form class
                class DummyTabularForm(SubmissionFieldFormMixin):
                    def __init__(self, value):
                        self.cleaned_data = {'value': value}
                        self.warnings = None
                        self._errors = {}
                        self.instance = None

                    def is_valid(self):
                        return True

                    @property
                    def errors(self):
                        return self._errors

                    def save(self, *args, **kwargs):
                        # just a dummy
                        pass

                form = DummyTabularForm(value=None)
            self._form_fields.append({'field': field, 'form': form})

        return self._form_fields

    def get_forms_with_tables(self):
        """
            Breaks up the forms into forms and subforms (in tables)
        """
        if hasattr(self, '_form_field_list_with_tables'):
            return self._form_field_list_with_tables

        self._form_field_list_with_tables = []
        form_fields = self.get_submission_fields_and_forms()

        # go through all documentation fields for this credit
        for df in self.instance.credit.documentationfield_set.all():

            # create a table wrapper if it's a table
            if df.type == 'tabular':
                table_wrapper = {'tabular': True,
                                 'instance': {'documentation_field': df},
                                 'errors': False,
                                 'subforms': {}} # subforms are a dict for lookup purposes

                subfield_id_list = []
                for row in df.tabular_fields['fields']:
                    for cell in [cell for cell in row if cell != '']:
                        subfield_id_list.append(int(cell))

                # populate subforms and remove from all form_fields
                for sub_id in subfield_id_list:
                    # remove from base list
                    for f in form_fields:
                        if f['field'].documentation_field_id == sub_id:
                            table_wrapper['subforms']["%d" % sub_id] = f['form']
                            if f['form'].errors:
                                table_wrapper['errors'] = True
                            form_fields.remove(f)
                    # remove from new list, in case they are out of order
                    for f in self._form_field_list_with_tables:
                        if type(f) != dict and f.instance.documentation_field.id == sub_id:
                            table_wrapper['subforms']["%d" % sub_id] = f
                            if f.errors:
                                table_wrapper['errors'] = True
                            self._form_field_list_with_tables.remove(f)

                # add the dummy form for the table
                for f in form_fields:
                    if f['field'].documentation_field_id == df.id:
                        table_wrapper['form'] = f['form']
                        table_wrapper['field'] = f['field']

                self._form_field_list_with_tables.append(table_wrapper)

            else:
                for f in form_fields:
                    if f['field'].documentation_field_id == df.id:
                        self._form_field_list_with_tables.append(f['form'])
                        break

        return self._form_field_list_with_tables

    def save(self, commit=True):
        """
            Save the data in this form (update instance or create a
            new submission)

            @return: the updated CreditSubmission instance.
        """
        # This is a bit tricky: CreditSubmission object needs the new
        # form field values to calculate points, but the form fields
        # need the CS objet to be saved so they can store a foreign
        # key to it...
        for field in self.get_submission_fields_and_forms():
            field['field'] = field['form'].save(False)

        self.instance = super(CreditSubmissionForm, self).save(commit)

        for field in self.get_submission_fields_and_forms():
            # Ensure field form has the newly saved instance of the
            # CreditSubmission object
            if field['form'].__class__.__name__ != "DummyTabularForm":
                field['form'].instance.credit_submission = self.instance
                field['form'].save(commit)

        return self.instance

    def is_valid(self):
        """ Perform data validation on the form and return True if it
        all passes"""
        is_valid = True

        # Caution: validation order is, unfortunately, important here...
        #  the Submission Fields are validated fist, so their cleaned_data
        #  is available when we validate, and thus clean(), the Form itself.
        for field in self.get_submission_fields_and_forms():
            if not field['form'].is_valid():
                is_valid = False

        # use short-cut evaluation here so Form is not validated if
        # fields don't validate.
        return is_valid and super(CreditSubmissionForm, self).is_valid()

    def has_warnings(self):
        """ Returns True if this submission generated any warning
        messages during clean"""
        for field in self.get_submission_fields_and_forms():
            if field['form'].warnings:
                return True
        # assert:  none of the fields had warnings defined.
        return self.warnings

    def non_field_warnings(self):
        """ Returns formatted 'top-level' warnings (not associated
        with any field) for this form"""
        return self.warnings.as_ul() if self.warnings else u''

    def _validate_required_fields(self):
        """ Helper to do required field validation.  Should only be
        called when submission is complete!"""
        __cleaned_data = self.cleaned_data
        for field in self.get_submission_fields_and_forms():
            # only try to evaluate the requirement if the field doesn't already
            # have errors
            if field['form'].is_valid():
                try:
                    form_value = field['form'].cleaned_data.get("value")
                    doc_field = field['field'].documentation_field
                    if doc_field.is_upload():   # require upload fields can be
                                                # blank so long as a file has
                                                # been previously uploaded
                        form_value = form_value or field['field'].get_value()
                    if (doc_field.is_required() and
                        form_value in (None, "", []) and
                        doc_field.type != 'tabular'):
                        field['form'].append_error( u"This field is required to "
                                                "mark this credit complete.")
                except AttributeError:
                    assert False

    def _has_errors(self):
        """ Helper method to determine if any error were discovered
        during basic validation of each field"""
        for field in self.get_submission_fields_and_forms():
            if "value" in field['form']._errors:
                return True
        # assert:  none of the fields had errors defined.
        return len(self.non_field_errors()) > 0

    def load_warnings(self):
        """
            Run custom validation to load any warnings onto the form

              - this is a bit sketchy b/c custom validation should
                only run once on a 'complete' instance, with no other
                basic validation errors.  CAREFUL!

              - call ONLY on GET (warnings are loaded by form
                validation on POST) for Complete instances!

            Loads warnings onto form and returns TRUE iff any warnings
            are loaded.
        """
        validation_errors, validation_warnings = (
            self.instance.credit.execute_validation_rules(self.instance))
        return self._load_warnings(validation_warnings)

    def _load_warnings(self, validation_warnings):
        """ Helper to eliminate duplicate code - warnings are loaded
        on both GET and POST"""
        has_warnings = False
        for field in self.get_submission_fields_and_forms():
            doc_field = field['field'].documentation_field
            if doc_field.identifier in validation_warnings:
                field['form'].append_warning(
                    validation_warnings[doc_field.identifier])
                has_warnings = True

        if 'top' in validation_warnings:
            self.warnings = WarningList([ validation_warnings['top'] ])
            has_warnings = True
        return has_warnings

    def _load_errors(self, validation_errors):
        """ Helper to load custom validation errors onto form """
        has_errors = False
        for field in self.get_submission_fields_and_forms():
            doc_field = field['field'].documentation_field
            if doc_field.identifier == "AY":
                pass
            if doc_field.identifier in validation_errors:
                field['form'].append_error(
                    validation_errors[doc_field.identifier])
                has_errors = True

        if 'top' in validation_errors:
            has_errors = True
        return has_errors

    def clean(self):
        """
            Assumes that a complete submission is being validated and cleaned.
        """
        cleaned_data = self.cleaned_data
        error_message = "This credit cannot be submitted as complete."

        self._validate_required_fields()
        has_error = self._has_errors()

        # only perform custom validation if the form had no basic
        # validation errors.  this is important because custom
        # validation_rules assume data is clean and complete.
        if not has_error:
            validation_errors, validation_warnings = (
                self.instance.credit.execute_validation_rules(self))
            has_error = self._load_errors(validation_errors)
            has_warning = self._load_warnings(validation_warnings)
            if 'top' in validation_errors:
                error_message = validation_errors['top']

        if has_error:
            raise forms.ValidationError(error_message)

        return cleaned_data

    def get_submission_field_key(self):
        """
            Returns a dictionary with identifier:value for each
            submission field on this form Should be analogous to
            CreditSubmission.get_submission_field_key
        """
        key = {}
        for field in self.get_submission_fields_and_forms():
            doc_field = field['field'].documentation_field
            key[doc_field.identifier] = field['form'].cleaned_data.get("value")
            if doc_field.is_upload():  # upload fields may be blank
                                       # but still have a file that's
                                       # been previously uploaded
                key[doc_field.identifier] = (key[doc_field.identifier] or
                                             field['field'].get_value())
        return key


class ResponsiblePartyForm(LocalizedModelFormMixin, ModelForm):
    """
        When adding a new Responsible Party
    """

    class Meta:
        model = ResponsibleParty
        exclude = ['institution']

    def form_name():
        return u"Responsible Party Form"
    form_name = staticmethod(form_name)

    def __init__(self, *args, **kwargs):
        super(ResponsiblePartyForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if self.fields[f].widget.__class__.__name__ == "TextInput":
                self.fields[f].widget.attrs.update({'size': 40})


class CreditUserSubmissionForm(CreditSubmissionForm):
    """
        A Credit Submission Form for a user submission, with Submission Status
    """
    submission_status = forms.CharField(widget=HiddenInput())
#     applicability_reason = forms.ModelChoiceField(
#         queryset=,
#         widget=HiddenInput()
#     )
                                        #forms.RadioSelect(
        #choices=CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED))
#     applicability_reason = custom_fields.ModelChoiceWithHelpField(
#         queryset=None, empty_label=None, required=False)

    class Meta:
        model = CreditUserSubmission
        fields = ['submission_notes', 'responsible_party_confirm',
                  'responsible_party', 'submission_status',
                  'applicability_reason']

    def __init__(self, *args, **kwargs):
        super(CreditUserSubmissionForm, self).__init__(*args, **kwargs)

        self.fields['applicability_reason'].queryset = self.instance.credit.applicabilityreason_set.all()
        self.fields['applicability_reason'].widget = HiddenInput()
        # if there are reasons that this might not apply, allow the
        # "not applicable" choice
#         if self.instance.credit.applicabilityreason_set.all():
# #             self.fields['applicability_reason'].queryset = (
# #                 self.instance.credit.applicabilityreason_set.all())
# #             self.fields['applicability_reason'].widget = HiddenInput()
# #             self.fields['submission_status'].widget = HiddenInput()
#             """forms.RadioSelect(
#                 choices=CREDIT_SUBMISSION_STATUS_CHOICES_W_NA,
#                 attrs={'onchange': 'toggle_applicability_reasons(this);'})"""

        self.fields['submission_notes'].widget.attrs['style'] = "width: 600px;"

        # Select only the responsible parties associated with that institution
        self.fields['responsible_party'].queryset = self.instance.subcategory_submission.category_submission.submissionset.institution.responsibleparty_set.all()

        self.fields['responsible_party_confirm'].label = mark_safe(
            '<span class="required_note" '
            '      title="This field is required to complete credit"> '
            '  * '
            '</span> '
            'The information included in the submission for this credit '
            'is accurate to the best of my knowledge.')

        for field in self:
            # add the onchange field_changed handler to inform users
            # of lost changes if a field already has an onchange
            # handler then just add to it.
            if field.field.widget.attrs.has_key('onchange'):
                field.field.widget.attrs['onchange'] = (
                    field.field.widget.attrs['onchange'] +
                    ';field_changed(this);')  # see include.js
            else:
                field.field.widget.attrs['onchange'] = 'field_changed(this);'

    def clean(self):
        """
            Submission status depends on status of required fields -
            can't submit as complete when its not!  An applicability
            reason must be selected if the submission status is set to
            'na'. Otherwise we want the reason to be None.
        """
        cleaned_data = self.cleaned_data
        status = cleaned_data.get("submission_status")
        reason = cleaned_data.get("applicability_reason")
        marked_complete = (status == 'c')
        error = False

        if not status :
            msg = u"Please tick the appropriate status for this submission."
            self._errors["submission_status"] = ErrorList([msg])
        if status == 'na' and not reason:
            msg = u"Please select a reason why this does not apply."
            self._errors["applicability_reason"] = ErrorList([msg])
            error = marked_complete # this is only an error if the
                                    # submission is marked complete.
        if not status == 'na':
            cleaned_data["applicability_reason"] = None

        # responsible party and responsible party confirm are required
        # if marked complete
        if marked_complete and self.instance.credit.requires_responsible_party:
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

        # Only perform the overall form validation if the submission
        # is marked complete and if the 
        if marked_complete:
            cleaned_data = super(CreditUserSubmissionForm, self).clean()

        return cleaned_data

    def has_responsible_party_error(self):
        """ Return True iff there is an error with the responsible
        party fields on this form"""
        return self._errors and \
               ("responsible_party" in self._errors or \
                "responsible_party_confirm" in self._errors)


class CreditUserSubmissionNotesForm(LocalizedModelFormMixin, ModelForm):
    """
        A Form for storing internal notes about a Credit Submission
    """
    internal_notes = forms.CharField(label="Only shared internally", widget=forms.Textarea(
        attrs={'style': "width: 600px;height: 300px;"}), required=False)

    class Meta:
        model = CreditUserSubmission
        fields = ['internal_notes', ]


class SubmitSubmissionSetForm(LocalizedModelFormMixin, ModelForm):
    """
        A Form to collect data for submitting a credit set for a rating
    """
    class Meta:
        model = SubmissionSet
        fields = ['reporter_status', 'submission_boundary', 'presidents_letter']

    def __init__(self, *args, **kwargs):
        super(SubmitSubmissionSetForm, self).__init__(*args, **kwargs)
        self.fields['presidents_letter'].required = True
        self.fields['submission_boundary'].required = True
        self.fields['submission_boundary'].label = (
            "Please describe the boundaries of the institution's "
            "STARS submission.  If any institution-owned, leased, "
            "or operated buildings or other holdings are omitted, "
            "briefly explain why.")


class BoundaryForm(LocalizedModelFormMixin, ModelForm):
    """
        A Form to update the boundary data for a submission
    """
    class Meta:
        model = SubmissionSet
        fields = ['submission_boundary',]

    def __init__(self, *args, **kwargs):
        super(BoundaryForm, self).__init__(*args, **kwargs)
        self.fields['submission_boundary'].required = True
        self.fields['submission_boundary'].label = (
            "Please describe the boundaries of the institution's "
            "STARS submission.  If any institution-owned, leased, "
            "or operated buildings or other holdings are omitted, "
            "briefly explain why.")
        self.fields['submission_boundary'].widget.attrs = {'cols': 60,
                                                           'rows': 4,}

class StatusForm(LocalizedModelFormMixin, ModelForm):
    """
        A Form to allow institutions to choose the Reporter status if
        they choose
    """
    class Meta:
        model = SubmissionSet
        fields = ['reporter_status',]


class LetterForm(LocalizedModelFormMixin, ModelForm):
    """
        A Form to accept the president's letter
    """
    class Meta:
        model = SubmissionSet
        fields = ['presidents_letter',]

    def clean_presidents_letter(self):
        data = self.cleaned_data['presidents_letter']
        if ('1-presidents_letter' in self.files.keys()
            and self.files['1-presidents_letter'].content_type != 'application/pdf'
            and not 'test' in sys.argv):
            raise forms.ValidationError("This doesn't seem to be a PDF file")
        return data

    def __init__(self, *args, **kwargs):
        super(LetterForm, self).__init__(*args, **kwargs)
        self.fields['presidents_letter'].required = True


class ExecContactForm(LocalizedModelFormMixin, ModelForm):
    """
        The contact informartion for the institution's executive contact
    """
    confirm = forms.BooleanField(
        label='I confirm that this is the highest ranking officer on campus.',
        required=True)

    class Meta:
        model = Institution
        fields = [ 'president_first_name',
                   'president_middle_name',
                   'president_last_name',
                   'president_title',
                   'president_address',
                   'president_city',
                   'president_state',
                   'president_zip' ]

    def __init__(self, *args, **kwargs):
        super(ExecContactForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].required = True
        self.fields['president_first_name'].label = "First Name"
        self.fields['president_middle_name'].label = "Middle Name"
        self.fields['president_middle_name'].required = False
        self.fields['president_last_name'].label = "Last Name"
        self.fields['president_title'].label = "Title"
        self.fields['president_address'].label = "Address"
        self.fields['president_city'].label = "City"
        self.fields['president_state'].label = "State"
        self.fields['president_zip'].label = "Zipcode"
