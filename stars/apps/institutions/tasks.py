from __future__ import absolute_import

from celery import shared_task

from .utils import update_institution_properties
from .models import Institution


@shared_task(name='institutions.monitor_subscription')
def monitor_subscription():
    update_institution_properties()


@shared_task(name='institutions.update_from_iss')
def update_from_iss():
    print "RUNNING Update from ISS"

    for i in Institution.objects.all():
        print i.name
        i.update_from_iss()
        i.save()
