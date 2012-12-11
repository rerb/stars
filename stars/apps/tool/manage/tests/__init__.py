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
                   SubscriptionPaymentOptionsViewTest)

from stars.apps.tool.tests.views import (SummaryToolViewTest,
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
    'PendingAccountDeleteViewTest': PendingAccountDeleteViewTest,
    'ResponsiblePartyCreateViewTest': ResponsiblePartyCreateViewTest,
    'ResponsiblePartyDeleteViewTest': ResponsiblePartyDeleteViewTest,
    'ResponsiblePartyEditViewTest': ResponsiblePartyEditViewTest,
    'ResponsiblePartyListViewTest': ResponsiblePartyListViewTest,
    'ShareDataViewTest': ShareDataViewTest,
    'SubscriptionPaymentOptionsViewTest': SubscriptionPaymentOptionsViewTest,
    'SubscriptionCreateViewTest': SubscriptionCreateViewTest,
    'SubscriptionPaymentCreateViewTest': SubscriptionPaymentCreateViewTest,
    'SummaryToolViewTest': SummaryToolViewTest,
    'ToolLandingPageViewTest': ToolLandingPageViewTest
    }
