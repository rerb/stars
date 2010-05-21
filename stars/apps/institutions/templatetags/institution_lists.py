from os.path import basename
from django import template
register = template.Library()

from stars.apps.submissions.models import SubmissionSet

@register.inclusion_tag('institutions/tags/latest_registrants.html')
def show_latest_registrants(count='5'):
    """ Display the (count) most recently registered institutions """
    
    inst_list = []
    for s in SubmissionSet.objects.all().filter(institution__enabled=True).filter(payment__isnull=False).exclude(payment__type='later').order_by('-date_registered')[0:count]:
        inst_list.append(s.institution)
        
    return {'inst_list': inst_list}