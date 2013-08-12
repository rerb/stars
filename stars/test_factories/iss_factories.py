import datetime
import time

import factory

from aashe.issdjango.models import Organizations


class OrganizationsFactory(factory.Factory):
    FACTORY_FOR = Organizations

    enabled = True
    slug = factory.Sequence(
        lambda i: 'test-inst-{0}-{1}'.format(i, time.time()))
    name = factory.Sequence(
        lambda i: 'test institution {0}.{1}'.format(i, time.time()))


class PendingAccountFactory(factory.Factory):
    FACTORY_FOR = PendingAccount

    institution = factory.SubFactory(InstitutionFactory)
    user_email = factory.Sequence(
        lambda i: 'testuser{0}{1}@example.com'.format(i, time.time()))


class StarsAccountFactory(factory.Factory):
    FACTORY_FOR = StarsAccount

    institution = factory.SubFactory(InstitutionFactory)
    user = factory.SubFactory(UserFactory)


class SubscriptionFactory(factory.Factory):
    FACTORY_FOR = Subscription

    institution = factory.SubFactory(InstitutionFactory)
    start_date = '1970-01-01'
    end_date = datetime.date.today()
    amount_due = 1000.00


class SubscriptionPaymentFactory(factory.Factory):
    FACTORY_FOR = SubscriptionPayment

    subscription = factory.SubFactory(SubscriptionFactory)
    date = datetime.date.today()
    amount = 50.00
    user = factory.SubFactory(UserFactory)
