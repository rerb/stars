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
def show_progress_icon(category, size_class=''):
    """ Displays a progress bar showing the percent complete """
    
    z = category.__class__.__name__
    
    measure_class = "progressBarMeasure"
    
    if z == 'int':
        # if the int is a percent
        numerator = ''
        denominator = ''
        bar_class = "progressBarSmall"
        content = ''
        caption = title = "%d%%" % category
        percentage = category
    else:
        numerator = category.get_finished_credit_count()
        denominator = category.get_total_credits()
        if numerator > 0:
            percentage = float(numerator)/float(denominator) * 100;
        else:
            percentage = 1.0 # Fix for css issues
        title = "%.0f / %.0f" % (numerator, denominator)
        
        if z == "CategorySubmission":
            bar_class = "progressBarLarge"
            if percentage < 50:
                measure_class = "progressBarMeasureRight"
                bar_class = "progressBarLargeRight"
                percentage = 100 - percentage
            content = "%.0f / %.0f" % (numerator, denominator)
            caption = "Credits Completed"
        elif z == "SubcategorySubmission":
            bar_class = "progressBarSmall"
            content = ""
            caption = "%.0f / %.0f Credits Completed" % (numerator, denominator)
    return {
        'percentage': percentage, 
        'numerator': numerator,
        'denominator': denominator,
        'size_class': size_class,
        'measure_class': measure_class,
        'bar_class': bar_class,
        'content': content,
        'caption': caption,
        'title': title,
    }

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
    icon.alt = payment.method
    icon.file, icon.title = PAYMENT_TYPE_ICONS.get(payment.method, (None, None))
    return {'icon': icon}


