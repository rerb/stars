import re
from datetime import date, timedelta
from django import template

deadline = date(year=2010, month=8, day=20)

register = template.Library()

@register.inclusion_tag('helpers/tags/countdown.html')
def charter_countdown():
    """ Returns the number of days until the charter participant registration deadline. """
    td = deadline - date.today()
    display = False
    title = None
    if td.days >= 0:
        display = True
    if td.days == 0:
        title = "Last Day"
    if td.days == 1:
        title = "1 day remaining"
    if td.days > 1:
        title = "%s days remaining" % td.days

    return {'display': display, 'title': title}
