from logging import getLogger

from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe
from django.core import urlresolvers

from stars.apps.helpers.models import BlockContent, SnippetContent

logger = getLogger('stars.user')

register = template.Library()

@register.inclusion_tag('helpers/tags/block_content.html')
def display_block_content(key, user=None):
    """ Simply returns the helptext, unstyled. """
    try:
        block = BlockContent.objects.get(key=key)
        edit_link = block.get_admin_url()
    except BlockContent.DoesNotExist:
        logger.warning("BlockContent, '%s', not found." % key,
                       extra={'user': user})
        block = ""
        edit_link = "%s?key=%s" % (
            urlresolvers.reverse('admin:helpers_blockcontent_add'), key)

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
        logger.warning("SnippetContent, '%s', not found." % key,
                       extra={'user': user})
        snippet = ""
        edit_link = "%s?key=%s" % (
            urlresolvers.reverse('admin:helpers_snippetcontent_add'), key)

    return {'snippet': snippet, 'user': user, 'edit_link': edit_link}
