from django.contrib import admin

from models import *

class SubmissionSetAdmin(admin.ModelAdmin):
    list_display = ('creditset', 'institution', 'date_registered', 'date_submitted', 'date_reviewed', 'rating')
    list_filter = ('institution',)
admin.site.register(SubmissionSet, SubmissionSetAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_filter = ("type",)
    list_display = ("institution", "amount", "date", "user", "type",)
admin.site.register(Payment, PaymentAdmin)

class CategorySubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(CategorySubmission, CategorySubmissionAdmin)

class SubcategorySubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(SubcategorySubmission, SubcategorySubmissionAdmin)

class CreditUserSubmissionAdmin(admin.ModelAdmin):
    list_filter = ("submission_status",)
    list_display = ("credit", "get_institution", "submission_status", "last_updated")
admin.site.register(CreditUserSubmission, CreditUserSubmissionAdmin)

class UploadSubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(UploadSubmission, UploadSubmissionAdmin)

class ResponsiblePartyAdmin(admin.ModelAdmin):
    pass
admin.site.register(ResponsibleParty, ResponsiblePartyAdmin)
