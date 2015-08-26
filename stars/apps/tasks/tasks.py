from __future__ import absolute_import

from celery import shared_task

from stars.apps.tasks.notifications import (
    send_welcome_email, send_overdue_notifications,
    send_post_submission_survey, send_renewal_reminder)


@shared_task(name='tasks.send_notifications')
def send_notifications():

    # Welcome
    print "Sending Welcome Emails"
    send_welcome_email()

    # Payment Reminders
    print "Sending overdue notifications"
    send_overdue_notifications()

    # After Submission
    print "Sending Post Submission Survey"
    send_post_submission_survey()

    # Renewal reminders
    print "Sending Renewal Reminders"
    send_renewal_reminder()
