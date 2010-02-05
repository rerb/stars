from os.path import basename
from django import template
register = template.Library()

from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import Payment

@register.inclusion_tag('institutions/tags/latest_registrants.html')
def show_latest_registrants(count='5'):
    """ Display the (count) most recently registered institutions """
    
    inst_list = []
    for p in Payment.objects.all().order_by('-id')[0:count]:
        inst_list.append(p.submissionset.institution)
        
    return {'inst_list': inst_list}