from django.forms import (BooleanField,
                          Form,
                          IntegerField,
                          ModelForm,
                          fields,
                          widgets)


class HiddenCounterForm(Form):
    """ Used to put a hidden counter on a form. """
    counter = IntegerField(initial=0, min_value=0, max_value=20,
                           widget=widgets.HiddenInput())


class Confirm(Form):
    """ Confirm an  operation. """
    confirm = BooleanField(required=True)


class LocalizedModelFormMixin(ModelForm):
    """ Mixin to make ModelForm fields localized.  Requires usual
        settings.py stuff (USE_L10N = True, USE_L10N = True,
        USE_THOUSAND_SEPARATOR = True, and
        django.middleware.locale.LocaleMiddleware in
        MIDDLEWARE_CLASSES).
    """
    LOCALIZED_FIELD_TYPES = (fields.DateField,
                             fields.DateTimeField,
                             fields.DecimalField,
                             fields.FloatField,
                             fields.IntegerField,
                             fields.TimeField)
    NUMBER_TYPES = (fields.FloatField, fields.IntegerField)

    def __new__(cls, *args, **kwargs):
        new_class = super(LocalizedModelFormMixin, cls).__new__(cls, *args,
                                                                **kwargs)
        for field_name, field in new_class.base_fields.items():
            if isinstance(field, cls.LOCALIZED_FIELD_TYPES):
                field.localize = True
                field.widget.is_localized = True
                if isinstance(field, cls.NUMBER_TYPES):
                    widget = widgets.TextInput()
                    extra_attrs = field.widget_attrs(widget)
                    if extra_attrs:
                        widget.attrs.update(extra_attrs)
                    field.widget = widget
        return new_class
