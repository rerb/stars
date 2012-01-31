from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe
from django.core import urlresolvers

import re

from stars.apps.helpers.models import BlockContent, SnippetContent
from stars.apps.helpers import watchdog

register = template.Library()

@register.inclusion_tag('helpers/tags/block_content.html')
def display_block_content(key, user=None):
    """ Simply returns the helptext, unstyled. """
    try:
        block = BlockContent.objects.get(key=key)
        edit_link = block.get_admin_url()
    except BlockContent.DoesNotExist:
        watchdog.log("lookup_block_content", "BlockContent, '%s', not found." % key, watchdog.WARNING)
        block = ""
        edit_link = "%s?key=%s" % (urlresolvers.reverse('admin:helpers_blockcontent_add'), key)
        
    return {'block': block, 'user': user, 'edit_link': edit_link}

@register.inclusion_tag('helpers/tags/snippet_content.html')
def display_snippet(key, user=None):
    """
        Simply returns the snippet text with an additional
        edit button if the user has privileges
    """
    try:
        snippet = SnippetContent.objects.get(key=key)
        edit_link = snippet.get_admin_url()
    except SnippetContent.DoesNotExist:
        watchdog.log("lookup_snippet_content", "SnippetContent, '%s', not found." % key, watchdog.WARNING)
        snippet = ""
        edit_link = "%s?key=%s" % (urlresolvers.reverse('admin:helpers_snippetcontent_add'), key)
        
    return {'snippet': snippet, 'user': user, 'edit_link': edit_link}
