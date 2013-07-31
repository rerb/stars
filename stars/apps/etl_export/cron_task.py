#!/usr/bin/env python

"""
    This script provides an access point for running the etl export utility from the command line
    
    usage: python manage.py execfile apps/etl_export/cron_task.py
"""

from stars.apps.etl_export.utils import update_etl

import sys
from datetime import datetime

print >> sys.stdout, "Started ETL Export: %s" % datetime.now()
update_etl()
print >> sys.stdout, "Completed ETL Export: %s" % datetime.now()
