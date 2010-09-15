from django.contrib import admin

from models import *

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'charter_participant')
admin.site.register(Institution, InstitutionAdmin)

class InstitutionStateAdmin(admin.ModelAdmin):
    pass
admin.site.register(InstitutionState, InstitutionStateAdmin)

class StarsAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'user_level')
    list_filter = ('institution',)
admin.site.register(StarsAccount, StarsAccountAdmin)

class PendingAccountAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'institution', 'user_level')
    list_filter = ('institution',)
    search_fields = ('user_email',)
admin.site.register(PendingAccount, PendingAccountAdmin)

class RegistrationReasonAdmin(admin.ModelAdmin):
    pass
admin.site.register(RegistrationReason, RegistrationReasonAdmin)

class RegistrationSurveyAdmin(admin.ModelAdmin):
    list_display = ('institution', 'primary_reason')
admin.site.register(RegistrationSurvey, RegistrationSurveyAdmin)
