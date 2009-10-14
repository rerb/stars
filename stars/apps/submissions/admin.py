from django.contrib import admin

from models import *

class RatingAdmin(admin.ModelAdmin):
    pass
admin.site.register(Rating, RatingAdmin)

class SubmissionSetAdmin(admin.ModelAdmin):
    list_display = ('creditset', 'institution', 'date_registered', 'date_submitted', 'date_reviewed', 'rating')
    list_filter = ('institution',)
admin.site.register(SubmissionSet, SubmissionSetAdmin)

class PaymentAdmin(admin.ModelAdmin):
    pass
admin.site.register(Payment, PaymentAdmin)

class InstitutionStateAdmin(admin.ModelAdmin):
    pass
admin.site.register(InstitutionState, InstitutionStateAdmin)

class CategorySubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(CategorySubmission, CategorySubmissionAdmin)

class SubcategorySubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(SubcategorySubmission, SubcategorySubmissionAdmin)

class CreditUserSubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(CreditUserSubmission, CreditUserSubmissionAdmin)

class UploadSubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(UploadSubmission, UploadSubmissionAdmin)