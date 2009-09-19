from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe 

from stars.apps.cms.models import ArticleMenu
from stars.apps.helpers import watchdog

register = template.Library()

@register.inclusion_tag('cms/tags/article_menu.html', takes_context=True)
def show_article_menu(context):
    """ Displays a list of article links in a hierarchy of sub-categories """
    article = None
    sub_category = None
    if ( context.has_key('article') ):
        article = context['article']
    if ( context.has_key('category') ) :
        sub_category = context['category']

    try:
        menu = ArticleMenu(sub_category)
        return {'mm_category':  menu.mm_category, 
                'sub_category': sub_category,
                'article_menu': menu,
                'current_article' : article }
    except Exception, e:
        watchdog.log_exception(e)
        return {}
    
@register.inclusion_tag('cms/tags/crumbs.html')
def show_cms_crumbs(object):
    """ Displays the crumb navigation for a particular article or category in the CMS """
    object_set = []
    parent = object
    while parent:
        object_set.insert(0, parent)
        parent = parent.get_parent()
    return {'object_set': object_set}
