import account_mixin, users
from aashe_auth_backend import AASHEAuthBackendTest
from submission_mixin import SubmissionMixinTest
from utils import UtilsTest
from views import ViewsTest

__test__ = {
    'account': account_mixin,
    'users': users,
    'AASHEAuthBackendTest': AASHEAuthBackendTest,
    'SubmissionMixinTest': SubmissionMixinTest,
    'UtilsTest': UtilsTest,
    'ViewsTest': ViewsTest
    }
