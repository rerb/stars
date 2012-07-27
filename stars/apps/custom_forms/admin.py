from django.contrib import admin

from models import *

class TAApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'institution', 'email', 'date_registered')
    list_filter = ('subcategories',)
admin.site.register(TAApplication, TAApplicationAdmin)

class EligibilityQueryAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'email', 'institution',)
admin.site.register(EligibilityQuery, EligibilityQueryAdmin)

class SteeringCommitteeNominationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'affiliation', 'email', 'date')
admin.site.register(SteeringCommitteeNomination, SteeringCommitteeNominationAdmin)

