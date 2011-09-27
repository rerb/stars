from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe
from django.core import urlresolvers

import re

from stars.apps.helpers.models import BlockContent
from stars.apps.helpers import watchdog

register = template.Library()

@register.inclusion_tag('helpers/tags/block_content.html')
def display_block_content(key, user=None):
    """ Simply returns the helptext, unstyled. """
    try:
        block = BlockContent.objects.get(key=key)
        edit_link = block.get_admin_url()
    except BlockContent.DoesNotExist:
        watchdog.log("lookup_block_content", "BlockContent, '%s', not found." % key)
        block = ""
        edit_link = "%s?key=%s" % (urlresolvers.reverse('admin:helpers_blockcontent_add'), key)
        
    return {'block': block, 'user': user, 'edit_link': edit_link}
