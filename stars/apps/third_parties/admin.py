from django.contrib import admin

from models import ThirdParty

class ThirdPartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'publication')
admin.site.register(ThirdParty, ThirdPartyAdmin)