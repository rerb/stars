from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models


def get_current_discounts():
    """
    Only current discounts.
    Can raise ValueDiscount.DoesNotExist exception.
    """
    return ValueDiscount.objects.filter(
        start_date__lte=date.today()).filter(end_date__gte=date.today())


def is_promo_code_current(code):
    """
    Checks if `code` matches a current discount.
    """
    return bool(code in [value_discount.code for value_discount
                         in get_current_discounts()])


class ValueDiscount(models.Model):

    code = models.CharField(unique=True,
                            max_length=36)
    amount = models.PositiveIntegerField(
        help_text='Discount Amount')
    percentage = models.PositiveIntegerField(
        default=0,
        help_text='Discount Percentage',
        validators=[MaxValueValidator(100)])
    start_date = models.DateField(help_text='Valid From')
    end_date = models.DateField(help_text='Valid Until')

    def __unicode__(self):
        return (u'code={code}, amount={amount}, '
                u'percentage={percentage} '
                u'start_date={start_date}, end_date={end_date}').format(
                    **self.__dict__)

    def _amount_or_percentage_required(self):
        """Ensure amount or percentage are specified.
        """
        if (self.amount == 0) and (self.percentage == 0):
            raise ValidationError("An amount or percentage must be specified.")
        return True

    def _amount_and_percentage_disallowed(self):
        """Ensure both amount and percentage are not specified.
        """
        if (self.amount > 0) and (self.percentage > 0):
            raise ValidationError("Only an amount or percentage can "
                                  "be specified, not both.")
        return True

    def _start_date_before_end_date(self):
        """Ensure start_date is before end_date.
        """
        if self.start_date > self.end_date:
            raise ValidationError("Start date can't be before end date.")
        return True

    def clean(self):
        return (self._amount_or_percentage_required() and
                self._amount_and_percentage_disallowed() and
                self._start_date_before_end_date())

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ValueDiscount, self).save(*args, **kwargs)
