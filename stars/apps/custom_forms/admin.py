from django.contrib import admin

from models import *

class TAApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'institution', 'email')
    list_filter = ('subcategories',)
admin.site.register(TAApplication, TAApplicationAdmin)