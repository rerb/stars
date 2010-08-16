"""
    Used to run the cron task for all notifications
    bin/django execfile stars/apps/tasks/notify_cron.py
"""

from datetime import datetime

from stars.apps.tasks.notifications import *

send_six_month_notifications(datetime.today())
send_overdue_notifications(datetime.today())