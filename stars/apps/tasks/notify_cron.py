"""
    Used to run the cron task for all notifications
    bin/django execfile stars/apps/tasks/notify_cron.py
"""

from datetime import datetime

from stars.apps.tasks.notifications import *

send_six_month_notifications()
send_overdue_notifications()
send_welcome_email()
send_post_submission_survey()
send_sixty_day_notifications()
send_thirty_day_notifications()
