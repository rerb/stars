from django.contrib import admin

from models import *

class TAApplicationAdmin(admin.ModelAdmin):
    pass
admin.site.register(TAApplication, TAApplicationAdmin)