import zipcodes
from test_survey import TestSurvey
from test_process import TestProcess
from views import ViewsTest, RegistrationSurveyViewTest
from .models import ModelsTopLevelTest, ValueDiscountTest

__test__ = {
    'zipcodes': zipcodes,
    'ModelsTopLevelTest': ModelsTopLevelTest,
    'TestSurvey': TestSurvey,
    'TestProcess': TestProcess,
    'ValueDiscountTest': ValueDiscountTest,
    'views': ViewsTest,
    'views': RegistrationSurveyViewTest
}
