from django.contrib import admin

from models import (SubmissionSet,
                    Boundary,
                    CategorySubmission,
                    DataCorrectionRequest,
                    SubcategorySubmission,
                    CreditUserSubmission,
                    UploadSubmission,
                    ResponsibleParty,
                    CreditSubmissionInquiry,
                    Flag,
                    SubmissionInquiry,
                    ExtensionRequest)
from stars.apps.credits.models import Rating


class SubmissionSetAdmin(admin.ModelAdmin):
    list_display = ('creditset', 'institution', 'date_registered',
                    'date_submitted', 'status', 'rating',
                    'is_locked', 'is_visible')
    list_filter = ('date_registered', 'status', 'is_locked')
    search_fields = ('institution__name',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(SubmissionSetAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            user_list = []
            for a in obj.institution.starsaccount_set.all():
                user_list.append(a.user)
            if obj.registering_user and obj.registering_user not in user_list:
                user_list.append(obj.registering_user)
            if obj.submitting_user and obj.submitting_user not in user_list:
                user_list.append(obj.submitting_user)
            choices = [(u.id, u.email) for u in user_list]
            form.base_fields['registering_user'].choices = choices
            form.base_fields['submitting_user'].choices = choices
        rating_choices = [(r.id, "%s (%s)" % (r.name, r.creditset.version)) for r in Rating.objects.all()]
        form.base_fields['rating'].choices = rating_choices

        form.base_fields['migrated_from'].choices = [(s.id, "%s" % s) for s in obj.institution.submissionset_set.all()]

        return form

admin.site.register(SubmissionSet, SubmissionSetAdmin)


class BoundaryAdmin(admin.ModelAdmin):
    list_display = ("submissionset",)
    search_fields = ('submissionset__institution__name',)
admin.site.register(Boundary, BoundaryAdmin)


class CategorySubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', "submissionset")
    list_filter = ('submissionset__institution',)
admin.site.register(CategorySubmission, CategorySubmissionAdmin)


class DataCorrectionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'reporting_field', 'date', 'approved')
    list_filter = ('approved',)
admin.site.register(DataCorrectionRequest, DataCorrectionRequestAdmin)


class SubcategorySubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(SubcategorySubmission, SubcategorySubmissionAdmin)


class CreditUserSubmissionAdmin(admin.ModelAdmin):
    list_filter = ("submission_status", 'credit')
    list_display = ("credit", "get_institution",
                    "submission_status", "last_updated")
admin.site.register(CreditUserSubmission, CreditUserSubmissionAdmin)


class UploadSubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(UploadSubmission, UploadSubmissionAdmin)


class ResponsiblePartyAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'institution', 'email')
    list_filter = ('institution',)
admin.site.register(ResponsibleParty, ResponsiblePartyAdmin)


class CreditSubmissionInquiryInline(admin.TabularInline):
    model = CreditSubmissionInquiry


class FlagAdmin(admin.ModelAdmin):
    model = Flag
admin.site.register(Flag, FlagAdmin)


class SubmissionInquiryAdmin(admin.ModelAdmin):
    list_display = ('date', 'anonymous', 'last_name',
                    'first_name', 'submissionset')
    inlines = [CreditSubmissionInquiryInline]
admin.site.register(SubmissionInquiry, SubmissionInquiryAdmin)


class ExtensionRequestAdmin(admin.ModelAdmin):
    list_display = ('submissionset', 'date', 'user')
    search_fields = ('user__username',)
admin.site.register(ExtensionRequest, ExtensionRequestAdmin)
