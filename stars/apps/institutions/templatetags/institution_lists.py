from os.path import basename
from datetime import date
from django import template
from django.conf import settings

register = template.Library()

from stars.apps.submissions.models import SubmissionSet
from stars.apps.institutions.models import Institution

@register.inclusion_tag('institutions/tags/latest_registrants.html')
def show_latest_registrants(count='5'):
    """ Display the (count) most recently registered institutions """

    inst_list = Institution.objects.filter(is_participant=True).filter(current_subscription__isnull=False).order_by("-current_subscription__start_date").distinct()[:count]

#    query_set = SubmissionSet.objects.published().order_by('-date_registered').select_related("institution")
#
#    inst_list = []
#    for s in query_set[0:count]:
#        inst_list.append(s.institution)

    return {'inst_list': inst_list}

@register.inclusion_tag('institutions/tags/rated_list.html')
def show_rated_registrants(count='5'):
    """ Display the (count) most recently registered institutions """

    query_set = SubmissionSet.objects.get_rated().order_by(
        '-date_submitted').select_related("institution")

    return {'ss_list': query_set[0:count], 'STATIC_URL': settings.STATIC_URL}
