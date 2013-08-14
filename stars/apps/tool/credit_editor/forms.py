import sys

from django.forms import ModelForm
from django import forms
from django.forms import widgets
from django.forms.extras import widgets as extra_widgets

from stars.apps.credits.models import *
from stars.apps.submissions.models import CreditTestSubmission
from stars.apps.tool.my_submission.forms import CreditSubmissionForm
from widgets import TabularFieldEdit


class RightSizeInputModelForm(ModelForm):
    """A ModelForm upon which every TextInput and Textarea widget
    is sized according to its max_length.

    Asks Bootstrap to do the super sizing by adding 'input-xxlarge'
    to the class attribute of the widgets.
    """
    WIDGETS_TO_RIGHTSIZE = [widgets.TextInput,
                            widgets.Textarea]

    # Bootstrap input size classes
    WIDGET_SIZES = {(0, 6): 'input-mini',
                    (7, 9): 'input-small',
                    (10, 13): 'input-medium',
                    (14, 19): 'input-large',
                    (20, 24): 'input-xlarge',
                    (25, sys.maxint): 'input-xxlarge'}

    DEFAULT_WIDGET_SIZES = {widgets.TextInput: 'input-xlarge',
                            widgets.Textarea: 'input-xlarge'}

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.rightsize_widgets()

    def rightsize_widgets(self):
        """Adjusts the size of all widgets in WIDGETS_TO_RIGHTSIZE.
        """
        for field in self.fields.values():
            if any([isinstance(field.widget, widget_to_rightsize)
                    for widget_to_rightsize in self.WIDGETS_TO_RIGHTSIZE]):
                self.rightsize(field)

    def rightsize(self, field):
        """Adjust the size of `field`.widget."""
        size = self.get_right_size(field)
        field.widget.attrs['class'] = (field.widget.attrs.get('class', '') +
                                       size).strip()

    def get_right_size(self, field):
        """Returns the Bootstrap input class name appropriate for `field`."""
        if getattr(field, 'max_length', None):
            for range_, class_name in self.WIDGET_SIZES.items():
                if range_[0] <= field.max_length <= range_[1]:
                    return class_name
        else:
            return self.get_default_size(field)

    def get_default_size(self, field):
        for widget in self.DEFAULT_WIDGET_SIZES:
            if isinstance(field.widget, widget):
                return self.DEFAULT_WIDGET_SIZES[widget]


class CreditSetForm(RightSizeInputModelForm):
    release_date = forms.DateField(widget=extra_widgets.SelectDateWidget())

    class Meta:
        model = CreditSet
        exclude = ('scoring_method', 'tier_2_points', 'previous_version')


class NewCreditSetForm(CreditSetForm):
    class Meta:
        model = CreditSet


class CreditSetScoringForm(RightSizeInputModelForm):
    class Meta:
        model = CreditSet
        fields = ('scoring_method', 'tier_2_points')
        # exactly the fields excluded on CreditSetForm


class CreditSetRatingForm(RightSizeInputModelForm):
    minimal_score = forms.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = Rating
        exclude = ('creditset', 'previous_version')


class CategoryForm(RightSizeInputModelForm):
    class Meta:
        model = Category
        exclude = ('creditset', 'ordinal', 'max_point_value',
                   'previous_version')

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'size': 50})


class CategoryOrderForm(RightSizeInputModelForm):

    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'class': 'ordinal'}))
    id = forms.IntegerField(widget=widgets.HiddenInput())

    class Meta:
        model = Category
        fields = ('ordinal', 'id')


class SubcategoryForm(RightSizeInputModelForm):

    class Meta:
        model = Subcategory
        exclude = ('ordinal', 'max_point_value', 'previous_version')

    def __init__(self, *args, **kwargs):
        """ Only allow categories from the same creditset """
        super(SubcategoryForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = [
            (cat.id, cat.title) for cat in
            self.instance.category.creditset.category_set.all()
        ]
        self.fields['title'].widget.attrs.update({'size': 50})


class NewSubcategoryForm(RightSizeInputModelForm):

    class Meta:
        model = Subcategory
        exclude = ('ordinal', 'max_point_value', 'category',
                   'previous_version')


class SubcategoryOrderForm(RightSizeInputModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'class': 'ordinal'}))

    class Meta:
        model = Subcategory
        fields = ('ordinal',)


class CreditForm(RightSizeInputModelForm):
    title = forms.CharField(widget=widgets.TextInput(attrs={'size': '32'}))

    class Meta:
        model = Credit
        exclude = ('ordinal', 'formula', 'validation_rules', 'number',
                   'type', 'previous_version', 'identifier')

    def __init__(self, *args, **kwargs):
        super(CreditForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'size': 50})

        cs = self.instance.subcategory.category.creditset
        self.fields['subcategory'].queryset = Subcategory.objects.filter(
            category__creditset=cs)


class T2CreditForm(RightSizeInputModelForm):

    class Meta:
        model = Credit
        exclude = ('ordinal', 'formula', 'validation_rules', 'number',
                   'type', 'point_value', 'scoring', 'measurement',
                   'previous_version')

    def __init__(self, *args, **kwargs):
        super(T2CreditForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'size': 50})


class NewCreditForm(CreditForm):

    class Meta(CreditForm.Meta):
        exclude = ('subcategory', 'ordinal', 'formula', 'number',
                   'validation_rules', 'type', 'previous_version',
                   'identifier')

    def __init__(self, *args, **kwargs):
        super(CreditForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'size': 50})


class NewT2CreditForm(NewCreditForm):

    class Meta(NewCreditForm.Meta):
        exclude = ('subcategory', 'ordinal', 'formula', 'validation_rules',
                   'number', 'type', 'point_value', 'scoring', 'measurement',
                   'previous_version', 'identifier')


class CreditFormulaForm(RightSizeInputModelForm):
    formula = forms.CharField(
        widget=widgets.Textarea(attrs={'class': 'noMCE',
                                       'cols': '70',
                                       'rows': '16'}),
        required=True)
    validation_rules = forms.CharField(
        widget=widgets.Textarea(
            attrs={'class': 'noMCE', 'cols': '70', 'rows': '16'}),
        required=False)

    class Meta:
        model = Credit
        fields = ('formula', 'validation_rules',)

    def clean_formula(self):
        return self._clean_code_field('formula')

    def clean_validation_rules(self):
        return self._clean_code_field('validation_rules')

    def _clean_code_field(self, key):
        code = self.cleaned_data[key]
        # remove any funky (Mac and MS) newlines and replace tabs with spaces
        code = code.replace("\r\n", "\n")
        code = code.replace("\t", "    ")
        (success, message) = compile_formula(code, key)
        if not success:
            raise forms.ValidationError(message)
        return code


class CreditTestSubmissionForm(CreditSubmissionForm):

    class Meta:
        model = CreditTestSubmission
        fields = ['expected_value']


class CreditOrderForm(RightSizeInputModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'class': 'ordinal'}))

    class Meta:
        model = Credit
        fields = ('ordinal',)


class DocumentationFieldForm(RightSizeInputModelForm):
    tooltip_help_text = forms.CharField(
        widget=widgets.Textarea(attrs={'rows': '2'}),
        required=False)
    inline_help_text = forms.CharField(
        widget=widgets.Textarea(attrs={'rows': '4'}),
        required=False)

    class Meta:
        model = DocumentationField
        exclude = ('ordinal', 'identifier', 'type', 'last_choice_is_other',
                   'previous_version')

    def __init__(self, *args, **kwargs):
        super(DocumentationFieldForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs["size"] = 60

        cs = self.instance.credit.get_creditset()
        self.fields['credit'].choices = cs.get_pulldown_credit_choices()
        fields = self.instance.credit.documentationfield_set.exclude(type='tabular')
        self.fields['tabular_fields'].widget = TabularFieldEdit(
                                             fields_in_credit=fields)

    def clean(self):
        cleaned_data = self.cleaned_data
        type = cleaned_data.get("type")

        #@todo: validate that choice-type fields actually specify choices

        # Code for cleaning numberic choices, if we ever implement those again...
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
        #                msg = u"Please provide choices or set this reporting field to 'user-defined'."
        #                self._errors["choices"] = ErrorList([msg])

        return cleaned_data


class NewDocumentationFieldForm(DocumentationFieldForm):
    class Meta(DocumentationFieldForm.Meta):
        exclude = ('ordinal', 'identifier', 'last_choice_is_other',
                   'min_range', 'max_range', 'previous_version')


class DocumentationFieldOrderingForm(RightSizeInputModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'size': '3', 'class': 'ordinal'}))
    value = forms.CharField()

    class Meta:
        model = DocumentationField
        fields = ('ordinal',)

    def __init__(self, *args, **kwargs):
        super(DocumentationFieldOrderingForm, self).__init__(*args, **kwargs)

        wKlass = self.instance.get_widget()
        self.fields['value'].widget = wKlass(
            attrs={'disabled': 'disabled', 'class': 'noMCE'})
        self.fields['value'].required = False
        if self.instance.type == 'choice':
            self.fields['value'].widget.choices = (
                (r.id, r.choice) for r in self.instance.choice_set.all()
            )


class ChoiceForm(RightSizeInputModelForm):
    class Meta:
        model = Choice
        fields = ('choice',)


class ChoiceOrderingForm(RightSizeInputModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'size': '3', 'class': 'ordinal'}))

    class Meta:
        model = Choice
        fields = ('ordinal', 'choice')


class ApplicabilityReasonForm(RightSizeInputModelForm):

    class Meta:
        model = ApplicabilityReason
        exclude = ('credit', 'ordinal', 'previous_version')

    def __init__(self, *args, **kwargs):
        super(ApplicabilityReasonForm, self).__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs['class'] = 'input-xxlarge'


class ApplicabilityReasonOrderingForm(RightSizeInputModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'size': '3', 'class': 'ordinal'}))

    class Meta:
        model = ApplicabilityReason
        fields = ('ordinal',)


class UnitForm(RightSizeInputModelForm):
    """
        When adding a new Credit Field Unit
    """
    class Meta:
        model = Unit
