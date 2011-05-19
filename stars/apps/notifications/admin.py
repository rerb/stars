from django.contrib import admin

from models import *

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title',)
    search_fields = ('title','description')
admin.site.register(EmailTemplate, EmailTemplateAdmin)