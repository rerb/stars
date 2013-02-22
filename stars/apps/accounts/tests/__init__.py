import account_mixin, users
from aashe_auth_backend import AASHEAuthBackendTest
from submission_mixin import SubmissionMixinTest
from utils import UtilsTest
from views import ViewsTest
from decorators import DecoratorsTest
from mixins import StarsMixinTest, AccountMixinTest

__test__ = {
    'account_mixin': account_mixin,
    'users': users,
    'AASHEAuthBackendTest': AASHEAuthBackendTest,
    'SubmissionMixinTest': SubmissionMixinTest,
    'UtilsTest': UtilsTest,
    'ViewsTest': ViewsTest,
    'DecoratorsTest': DecoratorsTest,
    'StarsMixinTest': StarsMixinTest,
    'AccountMixinTest': AccountMixinTest
    }
