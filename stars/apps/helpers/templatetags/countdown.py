import re
from datetime import date, timedelta
from django import template

from stars.apps.helpers import watchdog

deadline = date(year=2010, month=8, day=20)

register = template.Library()

@register.simple_tag
def charter_countdown():
    """ Returns the number of days until the charter participant registration deadline. """
    td = deadline - date.today()
    return td.days
