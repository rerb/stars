from django.utils.html import strip_spaces_between_tags, escape
from django import template
register = template.Library()


@register.inclusion_tag('tool/submissions/tags/available_points.html')
def format_available_points(creditsubmission, use_cache=False):
    """
        Displays the Available points in a readable formats
    """
    value = creditsubmission.get_available_points(use_cache=use_cache)
    adjusted_points = creditsubmission.get_adjusted_available_points()
    popup_text = None

    if adjusted_points == 0:
        value = None
        popup_text = "Total adjusted for non-applicable credits"

    elif creditsubmission.credit.point_variation_reason:
        popup_text = creditsubmission.credit.point_variation_reason

    return {'value': value,
            'popup_text': popup_text,
            "id": "%s_point_variation" % creditsubmission.id}


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
    
    if z == 'int':
        # if the int is a percent
        numerator = ''
        denominator = ''
        content = ''
        caption = title = "%d%%" % category
        percentage = category
    else:
        numerator = category.get_finished_credit_count()
        denominator = category.get_total_credits()
        if numerator > 0:
            percentage = float(numerator)/float(denominator) * 100;
        else:
            percentage = 0 # Fix for css issues
        title = "%.0f / %.0f" % (numerator, denominator)
        
        if z == "CategorySubmission":
            content = "%.0f / %.0f" % (numerator, denominator)
            caption = "Credits Completed"
        elif z == "SubcategorySubmission":
            content = ""
            caption = "%.0f / %.0f Credits Completed" % (numerator, denominator)
    return {
        'percentage': percentage, 
        'numerator': numerator,
        'denominator': denominator,
        'content': content,
        'caption': caption,
        'title': title,
    }

class Icon(object):
    __slots__ = ('title', 'file', 'alt', 'size_class')
    
@register.inclusion_tag('tool/submissions/tags/status_icon.html')
def show_status_icon(credit, white=0):
    """ Displays an icon representing credit status """
    from stars.apps.submissions.models import CREDIT_SUBMISSION_STATUS_ICONS
    title = credit.get_submission_status_display
    icon, alt = CREDIT_SUBMISSION_STATUS_ICONS.get(credit.submission_status, (None, None))
    return {'icon': icon, 'white': white, 'title': title}

@register.inclusion_tag('tool/submissions/tags/payment_icon.html')
def show_payment_type_icon(payment, size_class=''):
    """ Displays an icon representing the payment type """
    from stars.apps.submissions.models import PAYMENT_TYPE_ICONS
    icon = Icon()
    icon.size_class = size_class
    icon.alt = payment.method
    icon.file, icon.title = PAYMENT_TYPE_ICONS.get(payment.method, (None, None))
    return {'icon': icon}


