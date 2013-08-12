from .models import ModelsTopLevelTest, ValueDiscountTest
from .views import (RegistrationWizardLiveServerTest,
                    SurveyViewTest)

__test__ = {
    'ModelsTopLevelTest': ModelsTopLevelTest,
    'RegistrationWizardLiveServerTest': RegistrationWizardLiveServerTest,
    'SurveyViewTest': SurveyViewTest,
    'ValueDiscountTest': ValueDiscountTest
}
