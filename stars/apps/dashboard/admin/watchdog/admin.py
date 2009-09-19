from django.contrib import admin

from stars.apps.dashboard.admin.watchdog.models import WatchdogEntry

class WatchdogEntryAdmin(admin.ModelAdmin):
    list_display = ('severity', 'message', 'user', 'timestamp')

admin.site.register(WatchdogEntry, WatchdogEntryAdmin)


