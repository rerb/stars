import urlparse
from logging import getLogger, CRITICAL

import mock
from django.core import mail
from django.core.urlresolvers import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import TimeoutException

from stars.apps.institutions.models import (Institution,
                                            StarsAccount,
                                            Subscription,
                                            SubscriptionPayment)
from stars.apps.submissions.models import SubmissionSet
from stars.apps.tool.tests.views import InstitutionAdminToolMixinTest
from stars.test_factories.models import (OrganizationFactory,
                                         ValueDiscountFactory)

from .. import views

PARTICIPANT = 'participant'
RESPONDENT = 'respondent'

LATER = 'later'
NOW = 'now'

CONTACT_INFO = {'contact_first_name': u'Jimmy',
                'contact_last_name': u'Jonesy',
                'contact_title': u'Humble Servant',
                'contact_department': u'Refreshments',
                'contact_email': u'jimmy@jonestown.gy'}

EXECUTIVE_CONTACT_INFO = {
    'executive_contact_first_name': u'Jackie',
    'executive_contact_last_name': u'Mercer',
    'executive_contact_title': u'Master Blaster',
    'executive_contact_department': u'Combustibles',
    'executive_contact_email': u'haha@mercer.nom'}

# Don't bother me:
logger = getLogger('stars')
logger.setLevel(CRITICAL)


class CannotFindElementError(Exception):
    pass


class ForcedException(Exception):
    pass


class SurveyViewTest(InstitutionAdminToolMixinTest):

    view_class = views.SurveyView
