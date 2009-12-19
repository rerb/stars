from django.contrib import admin

from models import *

class HelpContextAdmin(admin.ModelAdmin):
    pass
admin.site.register(HelpContext, HelpContextAdmin)
