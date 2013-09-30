"""Tests for apps.tool.my_submission.views.
"""
from stars.apps.submissions import models as submissions_models
from stars.apps.tool.my_submission import views
from stars.apps.tool.tests.views import (InstitutionToolMixinTest,
                                         UserCanEditSubmissionMixinTest)
from stars.test_factories import (CategoryFactory,
                                  CategorySubmissionFactory,
                                  CreditFactory,
                                  CreditUserSubmissionFactory,
                                  DocumentationFieldFactory,
                                  DocumentationFieldSubmissionFactory,
                                  InstitutionFactory,
                                  StarsAccountFactory,
                                  SubcategoryFactory,
                                  SubcategorySubmissionFactory,
                                  SubmissionSetFactory)

# @TODO - we definitely need tests here for all the form submission tools

class SubmissionSummaryViewTest(InstitutionToolMixinTest):

    view_class = views.SubmissionSummaryView
    blessed_user_level = 'submit'  # user_level that should be allowed to GET
    blocked_user_level = 'view'  # user_level that should be blocked

    def setUp(self):
        super(SubmissionSummaryViewTest, self).setUp()
        self.institution = InstitutionFactory()
        self.account = StarsAccountFactory(institution=self.institution)
        self.request.user = self.account.user
        self.submission = SubmissionSetFactory(institution=self.institution)

    def test_get_succeeds(self, **kwargs):
        super(InstitutionToolMixinTest, self).test_get_succeeds(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))

    def test_get_is_blocked(self, **kwargs):
        super(InstitutionToolMixinTest, self).test_get_is_blocked(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))

    def test_success_url_is_loadable(self, **kwargs):
        super(InstitutionToolMixinTest, self).test_success_url_is_loadable(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))


class EditBoundaryViewTest(UserCanEditSubmissionMixinTest):

    view_class = views.EditBoundaryView


class CreditNotesViewTest(UserCanEditSubmissionMixinTest):

    view_class = views.CreditNotesView


class CreditHistoryViewTest(UserCanEditSubmissionMixinTest):

    view_class = views.CreditHistoryView

    def setUp(self, *args, **kwargs):
        super(CreditHistoryViewTest, self).setUp(*args, **kwargs)
        
        self.institution_slug = self.institution.slug

        submissionset = SubmissionSetFactory(
            institution=self.institution,
            status=submissions_models.RATED_SUBMISSION_STATUS)

        self.submissionset_id = str(submissionset.id)

        category = CategoryFactory()
        category_submission = CategorySubmissionFactory(
            category=category,
            submissionset=submissionset)
        self.category_abbreviation = category.abbreviation

        subcategory = SubcategoryFactory()
        subcategory_submission = SubcategorySubmissionFactory(
            subcategory=subcategory,
            category_submission=category_submission)
        self.subcategory_slug = subcategory.slug

        credit = CreditFactory()
        credit_submission = CreditUserSubmissionFactory(
            credit=credit,
            subcategory_submission=subcategory_submission)
        self.credit_identifier = credit.identifier

        # Some history to show:
        documentation_field = DocumentationFieldFactory(
            credit=credit)
        documentation_field_submission = DocumentationFieldSubmissionFactory(
            documentation_field=documentation_field,
            credit_submission=credit_submission)

    def test_get_succeeds(self, **kwargs):
        super(UserCanEditSubmissionMixinTest, self).test_get_succeeds(
            institution_slug=self.institution_slug,
            submissionset=self.submissionset_id,
            category_abbreviation=self.category_abbreviation,
            subcategory_slug=self.subcategory_slug,
            credit_identifier=self.credit_identifier)

    def test_get_is_blocked(self, **kwargs):
        super(UserCanEditSubmissionMixinTest, self).test_get_is_blocked(
            institution_slug=self.institution_slug,
            submissionset=self.submissionset_id,
            category_abbreviation=self.category_abbreviation,
            subcategory_slug=self.subcategory_slug,
            credit_identifier=self.credit_identifier)
