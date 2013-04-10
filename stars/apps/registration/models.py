from datetime import date

from django.db import models


class DiscountManager(models.Manager):

    def get_current(self):
        """ Only current discounts """
        return ValueDiscount.objects.filter(
            start_date__lte=date.today()).filter(end_date__gte=date.today())

    def is_code_current(self, code):
        """
           Checks if `code` matches a current discount.
        """
        return code in [value_discount.code for value_discount
                        in self.get_current()]


class ValueDiscount(models.Model):

    objects = DiscountManager()
    code = models.CharField(max_length=16)
    amount = models.IntegerField(
        help_text='Discount amount')
    percentage = models.IntegerField(
        help_text='Discount percentage')
    start_date = models.DateField(help_text='Valid From')
    end_date = models.DateField(help_text='Valid Until')

    def save(self, *args, **kwargs):
        """Ensure amount and percentage are not both specified.
        """
        if (self.amount > 0) and (self.percentage > 0):
            raise Exception("Only an amount or percentage can "
                            "be specified, not both.")
        else:
            super(ValueDiscount, self).save(*args, **kwargs)
