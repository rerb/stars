"""
	Django Choice with Other widgets
	Original ChoiceWithOther downloaded from: http://www.djangosnippets.org/snippets/863/
	... with a few modifications...
	Plus several variations on the theme:
	  - Select with Othe
	  - Multi-Select with Other
"""
from django import forms
from django.forms import widgets
from django.utils.encoding import StrAndUnicode, smart_unicode, force_unicode
from django.utils.safestring import mark_safe

from stars.apps.helpers import watchdog
from stars.apps.credits.models import Choice

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

	@todo: Add doc test

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
class ChoiceWithOtherSelectWidget(forms.MultiWidget):
    """MultiWidget for use with SelectWithOtherField."""
    def __init__(self, choices=(), units=None):
        widgets = [
            forms.Select(choices=choices),
            forms.TextInput
        ]
        super(ChoiceWithOtherSelectWidget, self).__init__(widgets)
        self.units = units

    def set_decompress_method(self, decompress):
    	""" This MUST be called before using the widget to set the method used to decompress field values. """
    	self.decompress = decompress
    	
    def _set_choices(self, choices):
    	""" When choices are set for this widget, we want to pass those along to the CheckboxSelectMultiple widget"""
    	self.widgets[0].choices = choices
    def _get_choices(self, choices):
    	""" When choices are set for this widget, we want to pass out the CheckboxSelectMultiple widget's choices"""
    	return self.widgets[0].choices
    choices = property(_get_choices, _set_choices)
    	
    def set_units(self, units):
    	self.units = units
    	
    def format_output(self, rendered_widgets):
        """Format the output by rendering the "other" choice just below the select widget."""
        if (self.units):
        	rendered_widgets[0] = "%s <label>%s</label>"%(rendered_widgets[0], self.units)
        	rendered_widgets[1] = "%s <label>%s</label>"%(rendered_widgets[1], self.units)
        	
        return "%s<br>%s"%(rendered_widgets[0], rendered_widgets[1])

class ModelChoiceWithOtherField(forms.ModelChoiceField):
    """
    ModelChoiceField for selecting Choice's, with an option for a user-submitted "other" Choice.

	Takes after a MultiField in many ways, but gains more from inheriting from ModelChoiceField 
	
	@todo: Add doc test
    """
    def __init__(self, model, *args, **kwargs):
        if kwargs.has_key('choices'):
            widget = ChoiceWithOtherSelectWidget(choices=kwargs['choices'])
            kwargs.pop('choices')
        else:
            widget = ChoiceWithOtherSelectWidget()
        	
        self._was_required = kwargs.pop('required', True)
        kwargs['required'] = False
        super(ModelChoiceWithOtherField, self).__init__(model, widget=widget, *args, **kwargs)

    def set_compress_methods(self, compress, decompress):
    	""" This MUST be called before using the field to set the methods used to compress and decompress field values. """
    	self.compress = compress
    	self.widget.set_decompress_method(decompress)
    	
    def set_units(self, units):
    	""" The units to display with each Choice """
    	self.widget.set_units(units)

    def clean(self, value):
    	""" May return a Choice object (for 'bonafide" choice selection, or a string for the 'other' value """
#    	return self.fields[0].clean(value)
        if value and not isinstance(value, list):
            raise forms.ValidationError('Invalid choice')
        if self._was_required and (not value or value[0] in (None, '')):
            raise forms.ValidationError(self.error_messages['required'])
        if not value:
            return None
        # clean the two physical fields...
        choice = super(ModelChoiceWithOtherField, self).clean(value[0]) 
        other_value = forms.fields.CharField(required=False).clean(value[1]) 
        
        return self.compress(choice, other_value)

"""
	Django CheckboxSelectMultiple Field with Other
	Based on above, but modified to use a CheckboxSelectMultiple rather than Radio
"""
class CheckboxSelectMultipleWithOtherWidget(forms.MultiWidget):
    """MultiWidget for use with CheckboxSelectWithOtherField."""
    def __init__(self, choices=()):
        widgets = [
            forms.CheckboxSelectMultiple(choices=choices),
            forms.TextInput
        ]
        super(CheckboxSelectMultipleWithOtherWidget, self).__init__(widgets)

    def set_decompress_method(self, decompress):
    	""" This MUST be called before using the widget to set the method used to decompress field values. """
    	self.decompress = decompress
    	
    def _set_choices(self, choices):
    	""" When choices are set for this widget, we want to pass those along to the CheckboxSelectMultiple widget"""
    	self.widgets[0].choices = choices
    def _get_choices(self, choices):
    	""" When choices are set for this widget, we want to pass out the CheckboxSelectMultiple widget's choices"""
    	return self.widgets[0].choices
    choices = property(_get_choices, _set_choices)

    def render(self, name, value, attrs=None):
    	""" Gotta override render to ensure value gets decompressed correctly 
    	    - MultiWidget won't decompress a value that is a list, which, of course, our value is!
    	"""
    	# the 'decompressed' value looks lie this:  [ [list, of, choices], u'other' ]
    	# the 'compressed' value is simply a list: [list. of, choices, with, other]
    	# the value needs to be decompressed if the first element is not a list!
        if isinstance(value, list) and len(value)>0 and not isinstance(value[0], list):
            value = self.decompress(value)

        return super(CheckboxSelectMultipleWithOtherWidget, self).render(name, value, attrs)
       
    def format_output(self, rendered_widgets):
        """Format the output by rendering the "other" choice into the last choice."""
    	# Unfortunately, CheckboxSelectMultiple doesn't usea a renderer like RadioSelect, so we have to hack a little here...
    	   # This hack assumes CheckboxSelectMultiple widget is rendered as a list;
    	   # We are trying to insert the 'other' field just before the last </li> tag, containing the 'other' choice.
    	   # If there are units with that last choice, then insert just before the units.
    	pre, tag, post = rendered_widgets[0].rpartition('</li>')
    	pre, span, units = pre.rpartition("<span class='units'>")
    	if span:
    		tag = "%s%s%s"%(span, units, tag)
    	rendered_widgets[0] = "%s %%s %s%s"%(pre,tag, post)
        return rendered_widgets[0] % rendered_widgets[1]

class ModelMultipleChoiceWithOtherField(forms.ModelMultipleChoiceField):
    """
    MultipleChoiceField with an option for a user-submitted "other" value.

    The last item in the choices array passed to __init__ is expected to be a choice for "other". This field's
    cleaned data is a tuple consisting of the choices the user made, and the "other" field typed in if the choice
    made was the last one.

 	@todo: Add doc test

    """
    def __init__(self, model, *args, **kwargs):
        if kwargs.has_key('choices'):
	        widget = CheckboxSelectMultipleWithOtherWidget(choices=kwargs['choices'])
	        kwargs.pop('choices')
        else:
	        widget = CheckboxSelectMultipleWithOtherWidget()
        
        self._was_required = kwargs.pop('required', True)
        kwargs['required'] = False
        super(ModelMultipleChoiceWithOtherField, self).__init__(model, widget=widget, *args, **kwargs)
        self.units = None

    def set_compress_methods(self, compress, decompress):
    	""" This MUST be called before using the field to set the methods used to compress and decompress field values. """
    	self.compress = compress
    	self.widget.set_decompress_method(decompress)
    	
    def set_units(self, units):
    	""" The units to display with each Choice """
    	self.units = units

    def label_from_instance(self, choice):
    	""" Add units to the choice """
    	label = super(ModelMultipleChoiceWithOtherField, self).label_from_instance(choice)
    	if self.units:
    		# Hack alert:  widget rendering depends on the units span tag!!!
    		return mark_safe("%s <span class='units'>%s</span>"%(label, self.units))
    	else:
    		return label
    	
    def clean(self, value): #@todo - actually clean the data and return the appropriate Choice!!
        if self._was_required and not value or value[0] in (None, ''):
            raise forms.ValidationError(self.error_messages['required'])
        if not value:
            choice_list = []
        else:
        	choice_list = value[0]
        # @todo: SHOULD CALL ON COMPRESS LOGIC IN THE MODEL!!!
        return super(ModelMultipleChoiceWithOtherField, self).clean(choice_list)


class ModelMultipleChoiceCheckboxField(forms.ModelMultipleChoiceField):
    """ Replaces the default ModelMultipleChoiceField widget with checkboxes"""

    def __init__(self, model, *args, **kwargs):
        if kwargs.has_key('choices'):
	        widget = widgets.CheckboxSelectMultiple(choices=kwargs['choices'])
	        kwargs.pop('choices')
        else:
	        widget = widgets.CheckboxSelectMultiple()
        super(ModelMultipleChoiceCheckboxField, self).__init__(model, widget=widget, *args, **kwargs)
        self.units = None
        
    def set_units(self, units):
    	""" The units to display with each Choice """
    	self.units = units

    def label_from_instance(self, choice):
    	""" Add units to the choice """
    	label = super(ModelMultipleChoiceCheckboxField, self).label_from_instance(choice)
    	if self.units:
    		return mark_safe("%s <span class='units'>%s</span>"%(label, self.units))
    	else:
    		return label