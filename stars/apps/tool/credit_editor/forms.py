import sys

from django.forms import ModelForm
from django import forms
from django.forms import widgets
from django.forms.extras import widgets as extra_widgets

from stars.apps.credits.models import *
from stars.apps.submissions.models import CreditTestSubmission
from stars.apps.tool.my_submission.forms import CreditSubmissionForm


class CreditSetForm(ModelForm):
    release_date = forms.DateField(widget=extra_widgets.SelectDateWidget())


    class Meta:
        model = CreditSet
        exclude = ('scoring_method', 'tier_2_points', 'previous_version')


class NewCreditSetForm(CreditSetForm):
    class Meta:
        model = CreditSet


class CreditSetScoringForm(ModelForm):
    class Meta:
        model = CreditSet
        fields = ('scoring_method', 'tier_2_points')
        # exactly the fields excluded on CreditSetForm


class CreditSetRatingForm(ModelForm):
    minimal_score = forms.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = Rating
        exclude = ('creditset', 'previous_version')


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        exclude = ('creditset', 'ordinal', 'max_point_value',
                   'previous_version')

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'size': 50})


class CategoryOrderForm(ModelForm):

    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'class': 'ordinal'}))
    id = forms.IntegerField(widget=widgets.HiddenInput())

    class Meta:
        model = Category
        fields = ('ordinal', 'id')


class SubcategoryForm(ModelForm):

    class Meta:
        model = Subcategory
        exclude = ('ordinal', 'max_point_value', 'previous_version')

    def __init__(self, *args, **kwargs):
        """ Only allow categories from the same creditset """
        super(SubcategoryForm, self).__init__(*args, **kwargs)
        print >> sys.stderr, "instance: %s" % self.instance
        self.fields['category'].choices = [
            (cat.id, cat.title) for cat in
            self.instance.category.creditset.category_set.all()
        ]
        self.fields['title'].widget.attrs.update({'size': 50})


class NewSubcategoryForm(ModelForm):

    class Meta:
        model = Subcategory
        exclude = ('ordinal', 'max_point_value', 'category',
                   'previous_version')


class SubcategoryOrderForm(ModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'class': 'ordinal'}))

    class Meta:
        model = Subcategory
        fields = ('ordinal',)


class CreditForm(ModelForm):
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


class T2CreditForm(ModelForm):

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


class CreditFormulaForm(ModelForm):
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


class CreditOrderForm(ModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'class': 'ordinal'}))

    class Meta:
        model = Credit
        fields = ('ordinal',)


class DocumentationFieldForm(ModelForm):
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


class DocumentationFieldOrderingForm(ModelForm):
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
            print >> sys.stderr, "CHOICES!!!"
            self.fields['value'].widget.choices = (
                (r.id, r.choice) for r in self.instance.choice_set.all()
            )


class ChoiceForm(ModelForm):
    class Meta:
        model = Choice
        fields = ('choice',)


class ChoiceOrderingForm(ModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'size': '3', 'class': 'ordinal'}))

    class Meta:
        model = Choice
        fields = ('ordinal', 'choice')


class ApplicabilityReasonForm(ModelForm):

    class Meta:
        model = ApplicabilityReason
        exclude = ('credit', 'ordinal', 'previous_version')

    def __init__(self, *args, **kwargs):
        super(ApplicabilityReasonForm, self).__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs['class'] = 'input-xxlarge'


class ApplicabilityReasonOrderingForm(ModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'size': '3', 'class': 'ordinal'}))

    class Meta:
        model = ApplicabilityReason
        fields = ('ordinal',)


class UnitForm(ModelForm):
    """
        When adding a new Credit Field Unit
    """
    class Meta:
        model = Unit
