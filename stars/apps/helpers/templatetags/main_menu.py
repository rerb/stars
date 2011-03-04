from django import template
from django.core.cache import cache
from django.conf import settings

from stars.apps.cms.models import Category

register = template.Library()

class menuItem:
    """
        Defines a single menu item 
    """
    def __init__(self, is_current, href, label):
        if (is_current):
            self.css_class="current"
        else:
            self.css_class=""
        self.href = href
        self.label = label
                

@register.inclusion_tag('helpers/tags/main_menu.html')
def show_main_menu(user=None, menu_category=None):
    """ 
        Displays the main menu with the current selection marked.
        Menu cannot be cached directly, since it is dynamic and depends on access level of user.
        Param:
            menu_category
                current category for the menu. May be an ArcitleCategory, a string, or None.
    """
    # Hide the main menu completely if the reporting tool is offline.
    # We may want to finesse this a little to allow access to public parts of the site later.
    if (settings.HIDE_REPORTING_TOOL or settings.MAINTENANCE_MODE) and (not user or not user.is_staff):
        return {'menu_items': []}

    # Menu order is primarily defined by Article Category ordinal
    # Exceptions:
    #    The second menu item is STARS Institutions app
    #    The last menu option, My Dashboard, is only added for authenticated users
    menuItems = []
    for category in Category.objects.all():
        if category.title != "Help":
            menuItems.insert(0, menuItem(category==menu_category, category.get_absolute_url(), category.title))
    
    # if user and user.is_staff:  # currently, restrict this item to staff only, although it is designed to be public.
    menuItems.insert(1, menuItem(menu_category=="institutions", "/institutions/data-displays/dashboard/", "STARS Institutions"))

    #if user and user.has_perm('tool'):
    menuItems.insert(0, menuItem(menu_category=="tool", "/tool/", "Reporting Tool"))
    
    return {'menu_items': menuItems} 
