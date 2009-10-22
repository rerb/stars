from django import template
#from django import forms
#from django.forms import widgets
#from django.utils.html import strip_spaces_between_tags, escape

from stars.apps.submissions.models import DocumentationFieldSubmission
from stars.apps.dashboard.submissions.forms import SubmissionFieldForm
#import re

register = template.Library()

@register.inclusion_tag('dashboard/submissions/tags/documentation_field_form.html')
def show_field_form(doc_field):
    """ Displays the submission form for a documentation field """
    SubmissionFieldModelClass = DocumentationFieldSubmission.get_field_class(doc_field)
    submission_field = SubmissionFieldModelClass(documentation_field=doc_field) if SubmissionFieldModelClass else None
                    
    SubmissionFieldFormClass = SubmissionFieldForm.get_form_class(submission_field)
    form = SubmissionFieldFormClass(None, instance=submission_field)
    form.fields['value'].widget.attrs={'class': 'noMCE', 'disabled':'disabled'} # BUG!  If you take noMCE out here, things get weird!
    return{"documentation_field":doc_field, "field_form":form }
    

@register.inclusion_tag('dashboard/credit_editor/tags/crumbs.html')
def show_editor_crumbs(object):
    """ Displays the crumb navigation for a particular object in the Credit Editor """
    object_set = []
    parent = object
    while parent:
        object_set.insert(0, parent)
        parent = parent.get_parent()
    return {'object_set': object_set}

@register.inclusion_tag('dashboard/credit_editor/tags/dependent_objects.html')
def show_dependent_objects(object, depth=-1):
    """ 
        Displays a list of dependents of the given Credit model object to the given depth (-1 for all)
        This tag is recursive - it displays the dependency hierarchy to the given depth.
        If a depth is given, the depth'th level (when depth==1) is shown as counts only. 
    """
    dependents = [(None,[])]
    if hasattr(object, 'get_dependents'):
        dependents = object.get_dependents()
    return {'dependents': dependents, 'depth':depth-1, 'counts_only':depth==1} 
