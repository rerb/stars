from datetime import date, timedelta
import uuid

import factory

from stars.apps.registration.models import ValueDiscount


class ValueDiscountFactory(factory.Factory):
    FACTORY_FOR = ValueDiscount

    code = factory.LazyAttribute(lambda *args: str(uuid.uuid1())[:16])

    # This discount is, by default, in effect starting yesterday . . .
    start_date = factory.LazyAttribute(
        lambda *args: date.today() - timedelta(days=1))
    # . . . and ending tomorrow:
    end_date = factory.LazyAttribute(
        lambda *args: date.today() + timedelta(days=1))

    amount = 50
