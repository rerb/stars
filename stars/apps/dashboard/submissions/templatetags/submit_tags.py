from django.utils.html import strip_spaces_between_tags, escape
from django import template
register = template.Library()

@register.inclusion_tag('dashboard/submissions/tags/available_points.html')
def format_available_points(object):
    """
        Displays the Available points in a readable format
        this prevents mulitple quieries to the DB
    """
    available_points = object.get_available_points()
    adjusted_points = object.get_adjusted_available_points()
    if available_points == adjusted_points:
        adjusted_points = None
    return {'available_points': available_points, 'adjusted_points': adjusted_points}


@register.inclusion_tag('dashboard/submissions/tags/crumbs.html')
def show_submit_crumbs(object):
    """ Displays the crumb navigation for a particular object in the Submission Tool """
    object_set = []
    parent = object
    while parent:
        object_set.insert(0, parent)
        parent = parent.get_parent()
        
    return {'object_set': object_set}

@register.inclusion_tag('dashboard/submissions/tags/progress_icon.html')
def show_progress_icon(percent_complete, size_class=''):
    """ Displays a progress bar showing the percent complete """
    print "creating progress bar for %s%%, size: %s"%(percent_complete, size_class)
    return {'in_progress': percent_complete>0, 'complete' : percent_complete==100,
            'size_class': size_class, 'percent_complete': percent_complete}