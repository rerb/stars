import unittest

import django.contrib.auth

from stars.test_factories import institutions_factories
from stars.apps import institutions


class ClimateZoneFactoryTest(unittest.TestCase):

    def test_production(self):
        """Is a ClimateZone produced?"""
        climate_zone = institutions_factories.ClimateZoneFactory()
        self.assertIsInstance(climate_zone,
                              institutions.models.ClimateZone)
        

class InstitutionFactoryTest(unittest.TestCase):

    def test_name_is_unique(self):
        """Do the Institutions produced have unique names?"""
        first_institution = institutions_factories.InstitutionFactory()
        second_institution = institutions_factories.InstitutionFactory()
        self.assertNotEqual(first_institution.name,
                            second_institution.name)


class PendingAccountFactoryTest(unittest.TestCase):

    def test_institution_is_created(self):
        """Is an institution created for a new PendingAccount?"""
        pending_account = institutions_factories.PendingAccountFactory()
        self.assertIsInstance(pending_account.institution,
                              institutions.models.Institution)


class StarsAccountFactoryTest(unittest.TestCase):

    def test_institution_is_created(self):
        """Is an institution created for a new StarsAccount?"""
        stars_account = institutions_factories.StarsAccountFactory()
        self.assertIsInstance(stars_account.institution,
                              institutions.models.Institution)

    def test_user_is_created(self):
        """Is an user created for a new StarsAccount?"""
        stars_account = institutions_factories.StarsAccountFactory()
        self.assertIsInstance(stars_account.user,
                              django.contrib.auth.models.User)


class SubscriptionFactoryTest(unittest.TestCase):

    def test_institution_is_created(self):
        """Is an institution created for a new Subscription?"""
        subscription = institutions_factories.SubscriptionFactory()
        self.assertIsInstance(subscription.institution,
                              institutions.models.Institution)


class SubscriptionPaymentFactory(unittest.TestCase):

    def test_subscription_is_created(self):
        """Is an subscription created for a new SubscriptionPayment?"""
        subscription_payment = (
            institutions_factories.SubscriptionPaymentFactory())
        self.assertIsInstance(subscription_payment.subscription,
                              institutions.models.Subscription)

    def test_subscription_created_has_institution(self):
        """Is an institutution created for the subscription that's created?
        """
        subscription_payment = (
            institutions_factories.SubscriptionPaymentFactory())
        self.assertIsInstance(subscription_payment.subscription.institution,
                              institutions.models.Institution)
    
