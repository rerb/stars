#!/usr/bin/env python

"""
    This script provides an access point for running the etl export utility from the command line
    
    usage: python manage.py execfile apps/etl_export/cron_task.py
"""

from stars.apps.etl_export.utils import update_etl

update_etl()