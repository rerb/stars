from stars.apps.submissions.tests import scoring
from submission_manager import ManagerTest
from data_corrections import DataCorrectionTest

from stars.apps.submissions.newapi.test import (
    SubmissionSetResourceTestCase,
    CategorySubmissionResourceTestCase,
    SubcategorySubmissionResourceTestCase,
    CreditSubmissionResourceTestCase,
    DocumentationFieldSubmissionResourceTestCase)

from fixtures import FixturesTest

from categorysubmission import CategorySubmissionTest
from creditsubmission import CreditSubmissionTest
from choicewithothersubmission import ChoiceWithOtherSubmissionTest
from multichoicewithothersubmission import MultiChoiceWithOtherSubmissionTest
from numericsubmission import NumericSubmissionTest
from responsibleparty import ResponsiblePartyTest
from submissionset import SubmissionSetTest
from tasks import TasksTest
from views import TestSubmissionStructureMixin
from metric_conversion import MetricConversionTest
