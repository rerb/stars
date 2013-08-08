from logging import getLogger

from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe
from django.core import urlresolvers

from twitter import *
from django.conf import settings

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
        logger.info("BlockContent, '%s', not found." % key,
                       extra={'user': user})
        block = ""
        edit_link = "%s?key=%s" % (
            urlresolvers.reverse('admin:helpers_blockcontent_add'), key)

    return {'block': block, 'user': user, 'edit_link': edit_link}

@register.inclusion_tag('helpers/tags/twitter_feed.html')
def display_twitter_feed(account="aasheconference", count=2):
    """ Gets a list of tweets for an account. """
    t = Twitter(
            auth=OAuth(settings.OAUTH_TOKEN, settings.OAUTH_SECRET,
                settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
           )
    tweets = t.statuses.user_timeline(screen_name=account, count=count)

    return {'tweets': tweets}

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
