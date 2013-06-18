from renewal_tests import RenewalTest

from views import (AccountCreateViewTest, AccountDeleteViewTest,
                   AccountEditViewTest, AccountListViewTest,
                   ContactViewTest, InstitutionPaymentsViewTest,
                   MigrateDataViewTest, MigrateOptionsViewTest,
                   MigrateVersionViewTest,
                   PendingAccountDeleteViewTest,
                   ResponsiblePartyCreateViewTest,
                   ResponsiblePartyDeleteViewTest,
                   ResponsiblePartyEditViewTest,
                   ResponsiblePartyListViewTest, ShareDataViewTest,
                   SubscriptionCreateViewTest,
                   SubscriptionPaymentCreateViewTest,
                   SubscriptionPaymentOptionsViewTest,
                   SubscriptionPriceViewLiveServerTest,
                   SubscriptionPriceViewTest)

from stars.apps.tool.tests.views import (NoStarsAccountViewTest,
                                         SelectInstitutionViewTest,
                                         SummaryToolViewTest,
                                         ToolLandingPageViewTest)


__test__ = {
    'RenewalTest': RenewalTest,
    'AccountCreateViewTest': AccountCreateViewTest,
    'AccountDeleteViewTest': AccountDeleteViewTest,
    'AccountEditViewTest': AccountEditViewTest,
    'AccountListViewTest': AccountListViewTest,
    'ContactViewTest': ContactViewTest,
    'InstitutionPaymentsViewTest': InstitutionPaymentsViewTest,
    'MigrateDataViewTest': MigrateDataViewTest,
    'MigrateOptionsViewTest': MigrateOptionsViewTest,
    'MigrateVersionViewTest': MigrateVersionViewTest,
    'NoStarsAccountViewTest': NoStarsAccountViewTest,
    'PendingAccountDeleteViewTest': PendingAccountDeleteViewTest,
    'ResponsiblePartyCreateViewTest': ResponsiblePartyCreateViewTest,
    'ResponsiblePartyDeleteViewTest': ResponsiblePartyDeleteViewTest,
    'ResponsiblePartyEditViewTest': ResponsiblePartyEditViewTest,
    'ResponsiblePartyListViewTest': ResponsiblePartyListViewTest,
    'SelectInstitutionViewTest': SelectInstitutionViewTest,
    'ShareDataViewTest': ShareDataViewTest,
    'SubscriptionPaymentOptionsViewTest': SubscriptionPaymentOptionsViewTest,
    'SubscriptionCreateViewTest': SubscriptionCreateViewTest,
    'SubscriptionPaymentCreateViewTest': SubscriptionPaymentCreateViewTest,
    'SubscriptionPriceViewTest': SubscriptionPriceViewTest,
    'SubscriptionPriceViewLiveServerTest': SubscriptionPriceViewLiveServerTest,
    'SummaryToolViewTest': SummaryToolViewTest,
    'ToolLandingPageViewTest': ToolLandingPageViewTest
    }
