# m h  dom mon dow   command
"""
from starsapp

15 6 * * * /var/www/stars/tasks/subscription_monitor.sh
python manage.py execfile stars/apps/tasks/subscription_monitor.py
    - expire_ratings()
    - update_institution_properties()

0 3 * * * /var/www/stars/tasks/update_from_iss.py
python manage.py execfile stars/apps/tasks/update_from_iss.py

45 4 * * * /var/www/stars/tasks/pie_chart.py
python manage.py execfile stars/apps/submissions/cron.py
    - update_pie_api_cache()
    - expireRatings()

0 0 * * 0 /var/www/stars/tasks/cleanup
from django.core.management import call_command
call_command('my_command', 'foo', bar='baz')

15 4 * * * /var/www/stars/tasks/etl_export.py
python manage.py execfile stars/apps/etl_export/cron_task.py

0 5 * * * /var/www/stars/tasks/notify.py
python manage.py execfile stars/apps/tasks/notify_cron.py
"""

from celery.schedules import crontab
from datetime import timedelta
# 'schedule': timedelta(seconds=30), # testing

STARS_TASK_SCHEDULE = {

    # runs regularly to let us know celerybeat is working
    # 'run beacon': {
    #     'task': 'tasks.beacon',
    #     'schedule': timedelta(seconds=30),
    # },

    # Executes every morning at 6:15 A.M
    # stars.apps.institutions.tasks.monitor_subscription
    'monitor subscriptions every morning': {
        'task': 'institutions.monitor_subscription',
        'schedule': crontab(hour=6, minute=15),
        # 'schedule': timedelta(seconds=60),
    },
    # Executes every morning at 2am
    # stars.apps.submissions.tasks.load_subcategory_quartiles
    'load SubcategoryQuartiles table every morning': {
        'task': 'submissions.load_subcategory_quartiles',
        'schedule': crontab(hour=2, minute=0)
    },
    # Executes every morning at 3am
    # stars.apps.institutions.tasks.update_from_iss
    'update iss values every morning': {
        'task': 'institutions.update_from_iss',
        'schedule': crontab(hour=3, minute=0),
        # 'schedule': timedelta(seconds=60),
    },
    # Executes once a month
    # stars.config.celery.run_cleanup
    'clear expired sessions on the first of every month': {
        'task': 'tasks.run_cleanup',
        'schedule': crontab(0, 0, day_of_month='1'),
        # 'schedule': timedelta(seconds=60),
    },

    # # Executes once a month
    # # stars.apps.etl_export.tasks.update
    # 'Update the ETL models': {
    #     'task': 'etl_export.update',
    #     'schedule': crontab(0, 0, day_of_month='1'),
    # },

    # Executes every morning at 5am
    # stars.apps.tasks.tasks.send_notifications
    'send out notifications when necessary': {
        'task': 'tasks.send_notifications',
        'schedule': crontab(hour=7, minute=0),
        # 'schedule': timedelta(seconds=30),
    },
}
