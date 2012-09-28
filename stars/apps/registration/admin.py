from django.contrib import admin

from models import *

class ValueDiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'amount', 'start_date', 'end_date')
    
admin.site.register(ValueDiscount, ValueDiscountAdmin)
