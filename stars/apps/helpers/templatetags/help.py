from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe 

import re

from stars.apps.helpers.models import HelpContext

register = template.Library()

#@register.simple_tag
@register.inclusion_tag('helpers/tags/help_text.html')
def show_help_context(context_name, as_tooltip=True):
    """ Displays a tool-tip for the help text for the given context. """
    try:
        c = HelpContext.objects.get(name=context_name)
        help_text = c.help_text
    except:
        help_text = ""
    
    return {'help_text': _clean(help_text, as_tooltip), "tooltip": as_tooltip}

@register.inclusion_tag('helpers/tags/help_text.html')
def show_help_text(help_text, as_tooltip=True):
    """ Displays a tool-tip for the given help text with quotes properly escaped. """
    return {'help_text': _clean(help_text, as_tooltip), "tooltip": as_tooltip}

def _clean(text, as_tooltip):
    """ Helper to prepare the help text """
    js_encoded = escape(strip_spaces_between_tags(text.strip()))
    if as_tooltip:
        js_encoded = re.sub(r'\r\n|\r|\n', '', js_encoded)
        js_encoded = js_encoded.replace('&quot;', '\&quot;').replace("&amp;", '\&amp;').replace("&#39;", '\&#39;')
    return mark_safe(js_encoded)