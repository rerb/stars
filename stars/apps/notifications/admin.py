from django.contrib import admin

from models import *

class EmailInline(admin.TabularInline):
    model = CopyEmail
    
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title',)
    search_fields = ('title','description')
    inlines = [
        EmailInline,
    ]
admin.site.register(EmailTemplate, EmailTemplateAdmin)