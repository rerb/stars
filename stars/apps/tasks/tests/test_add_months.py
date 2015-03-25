"""
    >>> from stars.apps.tasks.notifications import add_months
    >>> import datetime

    >>> d = datetime.date(year=2010, month=4, day=30)
    >>> add_months(d, 2)
    datetime.date(2010, 6, 30)

    >>> add_months(d, 9)
    datetime.date(2011, 1, 30)

    >>> add_months(d, 35)
    datetime.date(2013, 3, 30)

    >>> add_months(d, -1)
    datetime.date(2010, 3, 30)

    >>> add_months(d, -2)
    datetime.date(2010, 2, 28)

    >>> add_months(d, -6)
    datetime.date(2009, 10, 30)

    >>> add_months(d, -18)
    datetime.date(2008, 10, 30)

"""

"""
    Doctests for the add_months method
"""
from django.test import TestCase

from stars.apps.tasks.notifications import add_months
from datetime import date

class AddMonthsTest(TestCase):

    def setUp(self):
        pass

    def test_adding(self):
        d = date(year=2010, month=10, day=1)

        d = add_months(d, 1)
        self.assertEqual(d, date(year=2010, month=11, day=1))

        d = add_months(d, 1)
        self.assertEqual(d, date(year=2010, month=12, day=1))

        d = add_months(d, 1)
        self.assertEqual(d, date(year=2011, month=1, day=1))

        d = add_months(d, 13)
        self.assertEqual(d, date(year=2012, month=2, day=1))

        d = add_months(d, -13)
        self.assertEqual(d, date(year=2011, month=1, day=1))

        d = add_months(d, -1)
        self.assertEqual(d, date(year=2010, month=12, day=1))
