"""
	Django Choice with Other widgets
	Original ChoiceWithOther downloaded from: http://www.djangosnippets.org/snippets/863/
	... with a few modifications...
	Plus several variations on the theme:
	  - Select with Othe
	  - Multi-Select with Other
"""
from django import forms
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.safestring import mark_safe

class ChoiceWithOtherRenderer(forms.RadioSelect.renderer):
    """RadioFieldRenderer that renders its last choice with a placeholder."""
    def __init__(self, *args, **kwargs):
        super(ChoiceWithOtherRenderer, self).__init__(*args, **kwargs)
        self.choices, self.other = self.choices[:-1], self.choices[-1]

    def __iter__(self):
        for input in super(ChoiceWithOtherRenderer, self).__iter__():
            yield input
        id = '%s_%s' % (self.attrs['id'], self.other[0]) if 'id' in self.attrs else ''
        label_for = ' for="%s"' % id if id else ''
        checked = '' if not force_unicode(self.other[0]) == self.value else 'checked="true" '
        yield '<label%s><input type="radio" id="%s" value="%s" name="%s" %s/> %s</label> %%s' % (
            label_for, id, self.other[0], self.name, checked, self.other[1])

class ChoiceWithOtherWidget(forms.MultiWidget):
    """MultiWidget for use with ChoiceWithOtherField."""
    def __init__(self, choices, units=None):
        widgets = [
            forms.RadioSelect(choices=choices, renderer=ChoiceWithOtherRenderer),
            forms.TextInput
        ]
        super(ChoiceWithOtherWidget, self).__init__(widgets)
        self.units = units

    def decompress(self, value):
        if not value:
            return [None, None]
        return value

    def set_units(self, units):
    	self.units = units
    	
    def format_output(self, rendered_widgets):
        """Format the output by substituting the "other" choice into the first widget."""
        if (self.units):
        	rendered_widgets[1] = "%s <label>%s</label>"%(rendered_widgets[1], self.units)
        	
        return rendered_widgets[0] % rendered_widgets[1]

class ChoiceWithOtherField(forms.MultiValueField):
    """
    ChoiceField with an option for a user-submitted "other" value.

    The last item in the choices array passed to __init__ is expected to be a choice for "other". This field's
    cleaned data is a tuple consisting of the choice the user made, and the "other" field typed in if the choice
    made was the last one.

    >>> class AgeForm(forms.Form):
    ...     age = ChoiceWithOtherField(choices=[
    ...         (0, '15-29'),
    ...         (1, '30-44'),
    ...         (2, '45-60'),
    ...         (3, 'Other, please specify:')
    ...     ])
    ...
    >>> # rendered as a RadioSelect choice field whose last choice has a text input
    ... print AgeForm()['age']
    <ul>
    <li><label for="id_age_0_0"><input type="radio" id="id_age_0_0" value="0" name="age_0" /> 15-29</label></li>
    <li><label for="id_age_0_1"><input type="radio" id="id_age_0_1" value="1" name="age_0" /> 30-44</label></li>
    <li><label for="id_age_0_2"><input type="radio" id="id_age_0_2" value="2" name="age_0" /> 45-60</label></li>
    <li><label for="id_age_0_3"><input type="radio" id="id_age_0_3" value="3" name="age_0" /> Other, please \
specify:</label> <input type="text" name="age_1" id="id_age_1" /></li>
    </ul>
    >>> form = AgeForm({'age_0': 2})
    >>> form.is_valid()
    True
    >>> form.cleaned_data
    {'age': (u'2', u'')}
    >>> form = AgeForm({'age_0': 3, 'age_1': 'I am 10 years old'})
    >>> form.is_valid()
    True
    >>> form.cleaned_data
    {'age': (u'3', u'I am 10 years old')}
    >>> form = AgeForm({'age_0': 1, 'age_1': 'This is bogus text which is ignored since I didn\\'t pick "other"'})
    >>> form.is_valid()
    True
    >>> form.cleaned_data
    {'age': (u'1', u'')}
    """
    def __init__(self, *args, **kwargs):
        fields = [
            forms.ChoiceField(widget=forms.RadioSelect(renderer=ChoiceWithOtherRenderer), *args, **kwargs),
            forms.CharField(required=False)
        ]
        widget = ChoiceWithOtherWidget(choices=kwargs['choices'])
        kwargs.pop('choices')
        self._was_required = kwargs.pop('required', True)
        kwargs['required'] = False
        super(ChoiceWithOtherField, self).__init__(widget=widget, fields=fields, *args, **kwargs)

    def compress(self, value):
        if self._was_required and not value or value[0] in (None, ''):
            raise forms.ValidationError(self.error_messages['required'])
        if not value:
            return [None, u'']
        return (value[0], value[1] if force_unicode(value[0]) == force_unicode(self.fields[0].choices[-1][0]) else u'')
       
"""
	Django Text Select Field with Other
	Based on above, but modified to use a Select rather than Radio
"""
class SelectWithOtherWidget(forms.MultiWidget):
    """MultiWidget for use with SelectWithOtherField."""
    def __init__(self, choices, units=None):
        widgets = [
            forms.Select(choices=choices),
            forms.TextInput
        ]
        super(SelectWithOtherWidget, self).__init__(widgets)
        self.units = units

    def decompress(self, value):
        if not value:
            return [None, None]
        return value

    def set_units(self, units):
    	self.units = units
    	
    def format_output(self, rendered_widgets):
        """Format the output by appending the "other" choice into the first widget."""
        if (self.units):
        	rendered_widgets[1] = "%s <label>%s</label>"%(rendered_widgets[1], self.units)
        	
        return "%s<br>%s"%(rendered_widgets[0], rendered_widgets[1])

class SelectWithOtherField(forms.MultiValueField):
    """
    SelectField with an option for a user-submitted "other" value.

    The last item in the choices array passed to __init__ is expected to be a choice for "other". This field's
    cleaned data is a tuple consisting of the choice the user made, and the "other" field typed in if the choice
    made was the last one.

    >>> class AgeForm(forms.Form):
    ...     age = SelectWithOtherField(choices=[
    ...         (0, '15-29'),
    ...         (1, '30-44'),
    ...         (2, '45-60'),
    ...         (3, 'Other, please specify:')
    ...     ])
    ...
    >>> # rendered as a RadioSelect choice field whose last choice has a text input
    ... print AgeForm()['age']
    <select id="id_age_0_0" name="age_0">
    <option value="0">15-29</option>
    <option value="1">30-44</option>
    <option value="2">45-60</option>
    <option value="3">Other, please specify:</option>
    </select><br><input type="text" name="age_1" id="id_age_1" /></li>
    >>> form = AgeForm({'age_0': 2})
    >>> form.is_valid()
    True
    >>> form.cleaned_data
    {'age': (u'2', u'')}
    >>> form = AgeForm({'age_0': 3, 'age_1': 'I am 10 years old'})
    >>> form.is_valid()
    True
    >>> form.cleaned_data
    {'age': (u'3', u'I am 10 years old')}
    >>> form = AgeForm({'age_0': 1, 'age_1': 'This is bogus text which is ignored since I didn\\'t pick "other"'})
    >>> form.is_valid()
    True
    >>> form.cleaned_data
    {'age': (u'1', u'')}
    """
    def __init__(self, *args, **kwargs):
        fields = [
            forms.ChoiceField(widget=forms.Select(), *args, **kwargs),
            forms.CharField(required=False)
        ]
        widget = SelectWithOtherWidget(choices=kwargs['choices'])
        kwargs.pop('choices')
        self._was_required = kwargs.pop('required', True)
        kwargs['required'] = False
        super(SelectWithOtherField, self).__init__(widget=widget, fields=fields, *args, **kwargs)

    def compress(self, value):
        if self._was_required and not value or value[0] in (None, ''):
            raise forms.ValidationError(self.error_messages['required'])
        if not value:
            return [None, u'']
        return (value[0], value[1] if force_unicode(value[0]) == force_unicode(self.fields[0].choices[-1][0]) else u'')

"""
	Django CheckboxSelectMultiple Field with Other
	Based on above, but modified to use a CheckboxSelectMultiple rather than Radio
"""
class CheckboxSelectMultipleWithOtherWidget(forms.MultiWidget):
    """MultiWidget for use with CheckboxSelectWithOtherField."""
    def __init__(self, choices, units=None):
        widgets = [
            forms.CheckboxSelectMultiple(choices=choices),
            forms.TextInput
        ]
        super(CheckboxSelectMultipleWithOtherWidget, self).__init__(widgets)
        self.units = units

    def decompress(self, value):
        if not value:
            return [None, None]
        return value

    def set_units(self, units):
    	self.units = units
   
#    def render(self, *args, **kwargs):
#    	elements = '\n'.split(output)
#    	elements.insert(-1,'%%s')  # add a placehoder so we can format in the 'other' field
#        return mark_safe(u'\n'.join(elements))
       
    def format_output(self, rendered_widgets):
        """Format the output by substituting the "other" choice into the first widget."""
        if (self.units):
        	rendered_widgets[1] = "%s <label>%s</label>"%(rendered_widgets[1], self.units)
        	
    	# Unfortunately, CheckboxSelectMultiple doesn't usea a renderer like RadioSelect, so we have to hack a little here...
    	   # This hack assumes CheckboxSelectMultiple widget is rendered as a list;
    	   # We are trying to insert the 'other' field just before the last </li> tag, containing the 'other' choice.
    	pre, tag, post = rendered_widgets[0].rpartition('</li>')
    	rendered_widgets[0] = "%s %%s %s%s"%(pre,tag, post)
        return rendered_widgets[0] % rendered_widgets[1]

class CheckboxSelectMultipleWithOtherField(forms.MultiValueField):
    """
    MultipleChoiceField with an option for a user-submitted "other" value.

    The last item in the choices array passed to __init__ is expected to be a choice for "other". This field's
    cleaned data is a tuple consisting of the choices the user made, and the "other" field typed in if the choice
    made was the last one.

    >>> class FavoritesForm(forms.Form):
    ...     activity = CheckboxSelectMultipleWithOtherField(choices=[
    ...         (0, 'Skiing'),
    ...         (1, 'Surfing'),
    ...         (2, 'Climbing'),
    ...         (3, 'Other, please specify:')
    ...     ])
    ...
    >>> # rendered as a RadioSelect choice field whose last choice has a text input
    ... print FavoritesForm()['activity']
    <ul>
    <li><label for="id_activity_0_0"><input type="checkbox" name="activity_0" value="0" id="id_activity_0_0" /> Skiing</label></li>
    <li><label for="id_activity_0_1"><input type="checkbox" name="activity_0" value="1" id="id_activity_0_1" /> Surfing</label></li>
    <li><label for="id_activity_0_2"><input type="checkbox" name="activity_0" value="2" id="id_activity_0_2" /> Climbing</label></li>
    <li><label for="id_activity_0_3"><input type="checkbox" name="activity_0" value="3" id="id_activity_0_3" /> Other, please specify:</label></li>
    <input type="text" name="activity_1" id="id_activity_1" />
    </ul>
    >>> form = FavoritesForm({'activity_0': (1,2)})
    >>> form.is_valid()
    True
    >>> form.cleaned_data
    {'activity': ([u'1', u'2'], u'')}
    >>> form = FavoritesForm({'activity_0': (0,3), 'activity_1': 'Skydiving'})
    >>> form.is_valid()
    True
    >>> form.cleaned_data
    {'activity': ([u'0', u'3'], u'Skydiving')}
    >>> form = FavoritesForm({'activity_0': (1,2), 'activity_1': 'This is bogus text which is ignored since I didn\\'t pick "other"'})
    >>> form.is_valid()
    True
    >>> form.cleaned_data
    {'activity': ([u'1', u'2'], u'')}
    """
    def __init__(self, *args, **kwargs):
        fields = [
            forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), *args, **kwargs),
#            forms.ChoiceField(widget=forms.Select(), *args, **kwargs),
            forms.CharField(required=False)
        ]
        widget = CheckboxSelectMultipleWithOtherWidget(choices=kwargs['choices'])
        kwargs.pop('choices')
        self._was_required = kwargs.pop('required', True)
        kwargs['required'] = False
        super(CheckboxSelectMultipleWithOtherField, self).__init__(widget=widget, fields=fields, *args, **kwargs)

    def compress(self, value):
        if self._was_required and not value or value[0] in (None, ''):
            raise forms.ValidationError(self.error_messages['required'])
        if not value:
            return [None, u'']
        return (value[0], value[1] if self.fields[0].choices[-1][0].__unicode__() in value[0] else u'')

