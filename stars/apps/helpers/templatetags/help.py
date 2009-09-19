from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe 

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
    return mark_safe(
             strip_spaces_between_tags( 
               text.strip().
               replace('"', '\&quot;' if as_tooltip else '&quot;').
               replace("'", '\&#39;'  if as_tooltip else '&#39;') 
             )
           )