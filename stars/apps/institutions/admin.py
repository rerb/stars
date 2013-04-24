from django.contrib import admin

from models import (Institution, StarsAccount,
                    PendingAccount, Subscription,
                    SubscriptionPayment, RegistrationReason,
                    RegistrationSurvey, RespondentRegistrationReason,
                    RespondentSurvey, ClimateZone)


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'aashe_id', 'enabled', 'charter_participant')
    list_filter = ('charter_participant', 'enabled')
    search_fields = ('name',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(InstitutionAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['current_submission'].queryset = obj.submissionset_set.all()
            form.base_fields['rated_submission'].queryset = obj.submissionset_set.all()
            form.base_fields['current_subscription'].queryset = obj.subscription_set.all()
        return form
admin.site.register(Institution, InstitutionAdmin)


class StarsAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'user_level')
    list_filter = ('institution',)
    search_fields = ('user__email',)
admin.site.register(StarsAccount, StarsAccountAdmin)


class PendingAccountAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'institution', 'user_level')
    list_filter = ('institution',)
    search_fields = ('user_email',)
admin.site.register(PendingAccount, PendingAccountAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('institution', 'start_date', 'end_date',
                    'ratings_allocated', 'ratings_used', 'paid_in_full')
    search_fields = ('institution__name',)
admin.site.register(Subscription, SubscriptionAdmin)


class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'method', 'date')
    search_fields = ('subscription__institution__name',)
admin.site.register(SubscriptionPayment, SubscriptionPaymentAdmin)


class RegistrationReasonAdmin(admin.ModelAdmin):
    pass
admin.site.register(RegistrationReason, RegistrationReasonAdmin)


class RegistrationSurveyAdmin(admin.ModelAdmin):
    list_display = ('institution', 'primary_reason')
admin.site.register(RegistrationSurvey, RegistrationSurveyAdmin)


class RespondentRegistrationReasonAdmin(admin.ModelAdmin):
    pass
admin.site.register(RespondentRegistrationReason, RespondentRegistrationReasonAdmin)


class RespondentSurveyAdmin(admin.ModelAdmin):
    list_display = ('institution', 'source')
admin.site.register(RespondentSurvey, RespondentSurveyAdmin)


class ClimateZoneAdmin(admin.ModelAdmin):
    pass
admin.site.register(ClimateZone, ClimateZoneAdmin)
