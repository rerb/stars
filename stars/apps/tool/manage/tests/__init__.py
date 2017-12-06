
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
                   SubscriptionCreateWizardLiveServerTest,)


from stars.apps.tool.tests.views import (NoStarsAccountViewTest,
                                         SelectInstitutionViewTest,
                                         SummaryToolViewTest,
                                         ToolLandingPageViewTest)


__test__ = {
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
    'SubscriptionCreateWizardLiveServerTest':
    SubscriptionCreateWizardLiveServerTest,
    'SummaryToolViewTest': SummaryToolViewTest,
    'ToolLandingPageViewTest': ToolLandingPageViewTest
    }
