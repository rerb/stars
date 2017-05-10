from __future__ import absolute_import

import logging
from celery import shared_task

from .utils import update_all_institution_properties
from .models import Institution


logger = logging.getLogger()


@shared_task(name='institutions.monitor_subscription')
def monitor_subscription():
    update_all_institution_properties()


@shared_task(name='institutions.update_from_iss')
def update_from_iss():
    for i in Institution.objects.all():
        i.update_from_iss()
        try:
            i.save()
        except Exception as exc:
            logger.error(
                "Can't save institution {}: {}".format(
                    i.name, exc))
