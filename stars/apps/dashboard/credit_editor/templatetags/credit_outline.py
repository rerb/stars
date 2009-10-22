from django import template

from stars.apps.credits.models import Subcategory, Credit

register = template.Library()

@register.inclusion_tag('dashboard/credit_editor/tags/credit_outline_object.html', takes_context=True)
def show_credit_outline_object(context, object):
    """ 
        Displays hierarchical outline (menu) for the given Credit model object
        This tag is recursive - it's template uses this tag to display child objects in the hierarchy.
    """
    # Credits are leaf nodes in the outline hierarchy
    is_leaf = isinstance(object, Credit)

    # Only one object should be 'current' - the lowest one in the hierarchy that appears in the context.
    category = context.get('category', None)
    subcategory = context.get('subcategory', None)
    credit = context.get('credit', None)
    is_current = category == object if not subcategory else \
                 subcategory == object if not credit else \
                 credit == object
    
    # One day, we may want to store the collapsed / expanded state in the session & fetch it from the user object here
    # For now - expand all in current category / subcategory, collapse all others.
    is_expanded = (category == object or subcategory == object)

     # Subcategories list their Tier1 and Tier2 credits separately
     # The 'more groups' concept could be generalized for other objects if needed in future.
    if isinstance(object, Subcategory):
        if hasattr(object, 'has_more_groups') and object.has_more_groups:  # display the additional group (tier 2 credits in this case)
            children = object.get_tier2_credits()
            object = 'Tier 2 Credits'
            is_expanded = credit in children
            is_current = False
        else:
            children = object.get_tier1_credits()
            object.has_more_groups = object.get_tier2_credits().count() > 0
    else:
        children = object.get_children()
    
    return { 'object': object, 
             'object_children': children,
             'is_label': isinstance(object, str),
             'is_leaf': is_leaf, 
             'is_current': is_current, 
             'is_expanded': is_expanded,
             'edit': context.get('edit', False),
             'category': category,
             'subcategory': subcategory,
             'credit': credit,
           }
