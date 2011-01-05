from os.path import basename
from datetime import date
from django import template

register = template.Library()

from stars.apps.submissions.models import SubmissionSet

@register.inclusion_tag('institutions/tags/latest_registrants.html')
def show_latest_registrants(count='5'):
    """ Display the (count) most recently registered institutions """
    
    query_set = SubmissionSet.objects.published().order_by('-date_registered')
    
    inst_list = []
    for s in query_set[0:count]:
        inst_list.append(s.institution)
        
    return {'inst_list': inst_list}

@register.inclusion_tag('institutions/tags/rated_list.html')
def show_rated_registrants(count='5'):
    """ Display the (count) most recently registered institutions """
    
    query_set = SubmissionSet.objects.get_rated().order_by('-date_submitted')
    
    return {'ss_list': query_set[0:count],}