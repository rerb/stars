from django.contrib import admin

from models import *

class SubmissionSetAdmin(admin.ModelAdmin):
    list_display = ('creditset', 'institution', 'date_registered', 'date_submitted', 'date_reviewed', 'rating')
    list_filter = ('submission_deadline','date_registered')
admin.site.register(SubmissionSet, SubmissionSetAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_filter = ("type",)
    list_display = ("get_institution", "amount", "date", "user", "type",)
admin.site.register(Payment, PaymentAdmin)

class CategorySubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', "submissionset")
    list_filter = ('submissionset__institution',)
admin.site.register(CategorySubmission, CategorySubmissionAdmin)

class DataCorrectionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'reporting_field', 'date','approved')
    list_filter = ('approved',)
admin.site.register(DataCorrectionRequest, DataCorrectionRequestAdmin)

class SubcategorySubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(SubcategorySubmission, SubcategorySubmissionAdmin)

class CreditUserSubmissionAdmin(admin.ModelAdmin):
    list_filter = ("submission_status", 'credit')
    list_display = ("credit", "get_institution", "submission_status", "last_updated")
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

class SubmissionInquiryAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'submissionset', 'date')
    inlines = [CreditSubmissionInquiryInline,]
admin.site.register(SubmissionInquiry, SubmissionInquiryAdmin)

class ExtensionRequestAdmin(admin.ModelAdmin):
    list_display = ('submissionset', 'date',)
admin.site.register(ExtensionRequest, ExtensionRequestAdmin)
