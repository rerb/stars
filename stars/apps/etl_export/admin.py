from django.contrib import admin

from models import *

class ETLAdmin(admin.ModelAdmin):
    list_display = ('institution', 'participant_status',)
    list_filter = ('is_published', 'participant_status',)
admin.site.register(ETL, ETLAdmin)