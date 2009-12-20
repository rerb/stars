from django.utils.html import strip_spaces_between_tags, escape
from django import template
register = template.Library()

@register.inclusion_tag('tool/submissions/tags/available_points.html')
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


@register.inclusion_tag('tool/submissions/tags/crumbs.html')
def show_submit_crumbs(object):
    """ Displays the crumb navigation for a particular object in the Submission Tool """
    object_set = []
    parent = object
    while parent:
        object_set.insert(0, parent)
        parent = parent.get_parent()
        
    return {'object_set': object_set}

@register.inclusion_tag('tool/submissions/tags/progress_icon.html')
def show_progress_icon(percent_complete, size_class=''):
    """ Displays a progress bar showing the percent complete """
    return {'in_progress': percent_complete>0, 'complete' : percent_complete==100,
            'size_class': size_class, 'percent_complete': percent_complete}


class Icon(object):
    __slots__ = ('title', 'file', 'alt', 'size_class')
    
@register.inclusion_tag('tool/submissions/tags/status_icon.html')
def show_status_icon(credit, size_class=''):
    """ Displays an icon representing credit status """
    from stars.apps.submissions.models import CREDIT_SUBMISSION_STATUS_ICONS
    icon = Icon()
    icon.size_class = size_class
    icon.title = credit.get_submission_status_display
    icon.file, icon.alt = CREDIT_SUBMISSION_STATUS_ICONS.get(credit.submission_status, (None, None))
    return {'icon': icon}

@register.inclusion_tag('tool/submissions/tags/payment_icon.html')
def show_payment_type_icon(payment, size_class=''):
    """ Displays an icon representing the payment type """
    from stars.apps.submissions.models import PAYMENT_TYPE_ICONS
    icon = Icon()
    icon.size_class = size_class
    icon.alt = payment.get_type_display
    icon.file, icon.title = PAYMENT_TYPE_ICONS.get(payment.type, (None, None))
    return {'icon': icon}


