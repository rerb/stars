from django.contrib import admin

from models import *
from forms import AdminWatchdogContactForm

class WatchdogEntryAdmin(admin.ModelAdmin):
    list_display = ('severity', 'message', 'user', 'timestamp')
    list_filter = ('severity',)

admin.site.register(WatchdogEntry, WatchdogEntryAdmin)

class WatchdogContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'alternate_email', 'severity')
    form = AdminWatchdogContactForm
    
admin.site.register(WatchdogContact, WatchdogContactAdmin)
