from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe 

import re

from stars.apps.helpers.models import BlockContent
from stars.apps.helpers import watchdog

register = template.Library()

@register.inclusion_tag('helpers/tags/block_content.html')
def display_block_content(key, user=None):
    """ Simply returns the helptext, unstyled. """
    try:
        block = BlockContent.objects.get(key=key)
    except:
        watchdog.log("lookup_block_content", "BlockContent, '%s', not found." % key)
        
    return {'block': block, 'user': user}
