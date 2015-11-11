from __future__ import absolute_import

from celery import shared_task

from .utils import expire_ratings, update_institution_properties
from .models import Institution


@shared_task(name='institutions.monitor_subscription')
def monitor_subscription():
    expire_ratings()
    update_institution_properties()


@shared_task(name='institutions.update_from_iss')
def update_from_iss():
    print "RUNNING Update from ISS"

    for i in Institution.objects.all():
        # o = i.profile
        # if i.name != o.org_name:
        print i.name
        # print "%s\n" % o.org_name
        i.update_from_iss()
        i.save()
