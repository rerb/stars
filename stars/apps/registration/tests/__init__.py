from .models import (  # AutomaticDiscountTest,
                     ModelsTopLevelTest,
                     ValueDiscountTest)
from .views import (  # RegistrationWizardLiveServerTest,
                    SurveyViewTest)

__test__ = {
    # Not doing payments in STARS anymore, so don't need to test
    # automatic discounts.
    # 'AutomaticDiscountTest': AutomaticDiscountTest,
    'ModelsTopLevelTest': ModelsTopLevelTest,
    # Not using registration wizard anymore, so don't need to test it,
    # but those tests are so nice I don't want to delete them.
    # 'RegistrationWizardLiveServerTest': RegistrationWizardLiveServerTest,
    'SurveyViewTest': SurveyViewTest,
    'ValueDiscountTest': ValueDiscountTest
}
