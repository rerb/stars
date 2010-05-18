from os.path import basename
import sys
from django import template
register = template.Library()

from stars.apps.credits.models import Choice

@register.inclusion_tag('institutions/tags/crumbs.html')
def show_scorecard_crumbs(object):
    """ Displays the crumb navigation for a particular object in the Reports Tool """
    # @todo: This is a duplicate of the submissions crumbs tag / template = only the link method differs
    object_set = []
    parent = object
    while parent:
        print >> sys.stderr, parent.__class__.__name__
        object_set.insert(0, parent)
        parent = parent.get_parent()
        
    return {'object_set': object_set}


@register.inclusion_tag('institutions/tags/reporting_field.html')
def show_reporting_field(field, hide_empty_field=False):
    """ 
        Displays a submission reporing field in the Reports Tool 
        Optionally, it will hide fields that do not have any value submitted 
    """
    format_method = { 
            'text': _get_text_context,
            'long_text': _get_text_context,
            'numeric': _get_text_context,
            'boolean': _get_boolean_context,
            'choice': _get_choice_context,
            'multichoice': _get_choice_context,
            'url': _get_url_context,
            'date': _get_date_context,
            'upload': _get_upload_context,
    }
    context = format_method.get(field.documentation_field.type, _get_text_context)(field)
    
    context.update({'show_field': ((not hide_empty_field) or (context['field_value'] is not None)),
                    'field': field
                   })
    
    return context

def _get_text_context(field):
    text = field.get_value()
    units = field.documentation_field.units
    return {'field_value' : text if text else None, 'units': units if (text and units) else ''}

def _get_date_context(field):
    date = field.get_value()
    return {'field_value' : date.strftime("%b. %d, %Y") if date else None}

def _get_boolean_context(field):
    value = field.get_value()
    return {'field_value' : 'Yes' if value else 'No' if value is not None else None}

def _get_url_context(field):
    url = field.get_value()
    if url:
        return {'url':url, 'field_value':url}
    else:
        return {'field_value':None}
    
def _get_upload_context(field):
    filepath = field.get_value()
    if filepath:
        filename = basename(str(filepath))
        url = filepath.url if filepath.url else ''
        return {'url':url, 'field_value':filename}
    else:
        return {'field_value':None}

def _get_choice_context(field):
    choices = list(Choice.objects.filter(documentation_field=field.documentation_field))
    if field.documentation_field.type == 'choice':  # for consistency, process single choice as a 1 element list
        field_choices = [field.get_value()]
    else:  # multi-choice fields have a list of values
        field_choices = field.get_value()
    
    # mark all the selected choices
    at_least_one_selected = False
    for choice in choices:
        if choice in field_choices:
            choice.is_selected = True
            at_least_one_selected = True  
        else:
            choice.is_selected = False
    
    units = field.documentation_field.units
    
    return {'choices': [ {'choice':c.choice, 'is_selected':c.is_selected} for c in choices ],
            'units' : units if units else '',
            'field_value': (True if at_least_one_selected else None)
           }
    
  