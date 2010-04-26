from django.contrib import admin

from models import *

class InstitutionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Institution, InstitutionAdmin)

class InstitutionStateAdmin(admin.ModelAdmin):
    pass
admin.site.register(InstitutionState, InstitutionStateAdmin)

class StarsAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'user_level')
admin.site.register(StarsAccount, StarsAccountAdmin)

class RegistrationReasonAdmin(admin.ModelAdmin):
    pass
admin.site.register(RegistrationReason, RegistrationReasonAdmin)

class RegistrationSurveyAdmin(admin.ModelAdmin):
    pass
admin.site.register(RegistrationSurvey, RegistrationSurveyAdmin)