from django.core.management.base import BaseCommand, CommandError

from stars.apps.tool.admin.watchdog.models import WatchdogEntry

from datetime import datetime, timedelta

class Command(BaseCommand):
    args = '<none>'
    help = 'Clears all entries older than a 30 days'

    def handle(self, *args, **options):
        
        td = timedelta(days=30)
        d = datetime.now() - td
        
        qs = WatchdogEntry.objects.filter(timestamp__lt=d)
        
        count = qs.count()
        print >> self.stdout, "Total Entries Cleared: %d" % count
        qs.delete()