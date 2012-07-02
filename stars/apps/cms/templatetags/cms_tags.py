from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe 

from stars.apps.cms.models import ArticleMenu
from stars.apps.helpers import watchdog

register = template.Library()

@register.inclusion_tag('cms/tags/article_menu.html', takes_context=True)
def show_article_menu(context):
    """ Displays a list of article links in a hierarchy of sub-categories """
    article = context['article'] if context.has_key('article') else None
    sub_category = context['category'] if context.has_key('category') else None
    root_category = context['root_category'] if context.has_key('root_category') else None
    
    try:
        menu = ArticleMenu(sub_category, root_category)
        return {'root_category':  menu.mm_category, 
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
