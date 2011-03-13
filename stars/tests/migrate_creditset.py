#!/usr/bin/env python

from stars.apps.institutions.models import *
from stars.apps.credits.models import *
from stars.apps.credits.utils import migrate_set

from datetime import date

cs = CreditSet.objects.get(pk=2)
new_cs = migrate_set(cs, '1.1', date(year=2011, month=2, day=9))
