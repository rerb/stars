from renewal_tests import RenewalTest
from views import ViewsTest, InstitutionPaymentsViewTest, \
     ResponsiblePartyCreateViewTest, ResponsiblePartyDeleteViewTest, \
     ResponsiblePartyListViewTest, ResponsiblePartyEditViewTest, \
     TopLevelFunctionsTest

__test__ = {
    'renewal_test': RenewalTest,
    'views': ViewsTest,
    'intitution_payments_view_test': InstitutionPaymentsViewTest,
    'responsible_party_view_test': ResponsiblePartyListViewTest,
    'responsible_party_edit_view_test': ResponsiblePartyEditViewTest,
    'responsible_party_create_view_test': ResponsiblePartyCreateViewTest,
    'responsible_party_delete_view_test': ResponsiblePartyDeleteViewTest,
    'top_level_functions_test': TopLevelFunctionsTest,
}
