from __future__ import absolute_import
from celery import shared_task
from .utils import update_etl
from datetime import datetime


@shared_task(name='etl_export.update')
def update():
    print "Started ETL Export: %s" % datetime.now()
    update_etl()
    print "Completed ETL Export: %s" % datetime.now()
