import time

import factory

from stars.apps.registration.models import ValueDiscount

class ValueDiscountFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ValueDiscount

    code = factory.Sequence(lambda i : 'code-{0}.{1}'.format(i, time.time()))
    amount = 50
