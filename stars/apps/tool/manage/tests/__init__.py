from renewal_tests import RenewalTest
from responsible_party_tests import ResponisblePartyTest
from views import ViewsTest, InstitutionPaymentsViewTest, \
     ResponsiblePartyListViewTest
from views import ResponsiblePartyEditViewTest

__test__ = {
    'renewal_test': RenewalTest,
    'responsible_party_test': ResponisblePartyTest,
    'views': ViewsTest,
    'intitution_payments_view_test': InstitutionPaymentsViewTest,
    'responsible_party_view_test': ResponsiblePartyListViewTest,
    'responsible_party_edit_view_test': ResponsiblePartyEditViewTest
}
