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

from calculated_field import CalculatedFieldTest
from categorysubmission import CategorySubmissionTest
from creditsubmission import CreditSubmissionTest
from creditsubmissionreviewnotation import CreditSubmissionReviewNotationTest
from choicewithothersubmission import ChoiceWithOtherSubmissionTest
from multichoicewithothersubmission import MultiChoiceWithOtherSubmissionTest
from numericsubmission import NumericSubmissionTest
from responsibleparty import ResponsiblePartyTest
from submissionset import SubmissionSetTest
from views import TestSubmissionStructureMixin

from filecache_tests import FileCacheTest
