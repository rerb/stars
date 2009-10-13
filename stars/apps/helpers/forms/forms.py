from django.forms import Form, widgets, IntegerField, BooleanField

""" Generic forms used by helpers. """

class HiddenCounterForm(Form):
    """ Used to put a hidden counter on a form """
    counter = IntegerField(initial=0, min_value=0, max_value=20, widget=widgets.HiddenInput())


class ConfirmDelete(Form):
    """ Confirm a deletion """
    confirm = BooleanField()
