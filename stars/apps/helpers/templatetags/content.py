from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe 

import re

from stars.apps.helpers.models import BlockContent
from stars.apps.helpers import watchdog

register = template.Library()

@register.simple_tag
def display_block_content(key):
    """ Simply returns the helptext, unstyled. """
    try:
        c = BlockContent.objects.get(key=key)
        return c.content
    except:
        watchdog.log("lookup_block_content", "BlockContent, '%s', not found." % key)
        return ""
