from datetime import date

from django.db import models

class DiscountManager(models.Manager):
    
    def get_current(self):
        """ Only current discounts """
        return ValueDiscount.objects.filter(start_date__lte=date.today()).filter(end_date__gte=date.today())

class ValueDiscount(models.Model):
    objects = DiscountManager()
    code = models.CharField(max_length=16)
    amount = models.IntegerField(help_text='Amount discounted from registration')
    start_date = models.DateField(help_text='Valid From')
    end_date = models.DateField(help_text='Valid Until')