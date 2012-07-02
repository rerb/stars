from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe 

import re

from stars.apps.helpers.models import HelpContext
from stars.apps.helpers import watchdog

register = template.Library()

def lookup_help_context(context_name):
    """ Pulls the help text from the DB if it's available """
    try:
        c = HelpContext.objects.get(name=context_name)
        return c.help_text
    except:
        watchdog.log("get_help_context", "HelpContext, '%s', not found." % context_name)
        return ""

@register.inclusion_tag('helpers/tags/help_text.html')
def show_help_context(context_name, as_tooltip=True):
    """ Displays a tool-tip for the help text for the given context. """
    help_text = lookup_help_context(context_name)
    
    return {'help_text': _clean(help_text, as_tooltip), "tooltip": as_tooltip}

@register.simple_tag
def get_help_context(context_name):
    """ Simply returns the helptext, unstyled. """
    help_text = lookup_help_context(context_name)

    return help_text

@register.inclusion_tag('helpers/tags/help_text.html')
def show_help_text(help_text, as_tooltip=True):
    """ Displays a tool-tip for the given help text with quotes properly escaped. """
    return {'help_text': _clean(help_text, as_tooltip), "tooltip": as_tooltip}

def _clean(text, as_tooltip):
    """ Helper to prepare the help text """
    if not text:
        return None
    js_encoded = strip_spaces_between_tags(text.strip())
    if as_tooltip:
        js_encoded = escape(js_encoded)
        js_encoded = re.sub(r'\r\n|\r|\n', '', js_encoded)
        js_encoded = js_encoded.replace('&quot;', '\&quot;').replace("&amp;", '\&amp;').replace("&#39;", '\&#39;')
    return mark_safe(js_encoded)
