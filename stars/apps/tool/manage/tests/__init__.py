from renewal_tests import RenewalTest
from responsible_party_tests import ResponisblePartyTest
from views import ViewsTest, InstitutionPaymentsViewTest, \
     ResponsiblePartyViewTest

__test__ = {
    'renewal_test': RenewalTest,
    'responsible_party_test': ResponisblePartyTest,
    'views': ViewsTest,
    'intitution_payments_view_test': InstitutionPaymentsViewTest,
    'responsible_party_view_test': ResponsiblePartyViewTest
}
