"""
    Used to run the cron task for all notifications
    bin/django execfile stars/apps/tasks/notify_cron.py
"""

from datetime import datetime

from stars.apps.tasks.notifications import *

# Welcome
send_welcome_email()

# Payment Reminders
send_overdue_notifications()

# Deadline Reminders
send_six_month_notifications()
send_three_month_notifications()
send_sixty_day_notifications()
send_thirty_day_notifications()

# After Submission
send_post_submission_survey()

# Renewal reminders
send_renewal_reminder()


