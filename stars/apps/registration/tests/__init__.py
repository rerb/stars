from .models import (AutomaticDiscountTest,
                     ModelsTopLevelTest,
                     ValueDiscountTest)
from .views import (RegistrationWizardLiveServerTest,
                    SurveyViewTest)

__test__ = {
    'AutomaticDiscountTest': AutomaticDiscountTest,
    'ModelsTopLevelTest': ModelsTopLevelTest,
    'RegistrationWizardLiveServerTest': RegistrationWizardLiveServerTest,
    'SurveyViewTest': SurveyViewTest,
    'ValueDiscountTest': ValueDiscountTest
}
