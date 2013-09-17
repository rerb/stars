"""Tests for apps.tool.my_submission.views.
"""
from stars.apps.tool.my_submission import views
from stars.apps.tool.tests.views import (InstitutionToolMixinTest,
                                         UserCanEditSubmissionMixinTest)
from stars.test_factories import (InstitutionFactory,
                                  StarsAccountFactory,
                                  SubmissionSetFactory,
                                  CategorySubmissionFactory,
                                  SubcategorySubmissionFactory,
                                  CreditUserSubmissionFactory,
                                  DocumentationFieldSubmissionFactory)


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
        self.category_submission = (
            self.submission.categorysubmission_set.all()[0])
        self.category_abbreviation = (
            self.category_submission.category.abbreviation)
        self.subcategory_submission = (
            self.category_submission.subcategorysubmission_set.all()[0])
        self.credit_user_submission = (
            self.subcategory_submission.creditusersubmission_set.all()[0])

    def test_get_succeeds(self, **kwargs):
        super(UserCanEditSubmissionMixinTest, self).test_get_succeeds(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id),
            category_abbreviation=self.category_abbreviation,
            subcategory_slug=self.subcategory_submission.subcategory.slug,
            credit_identifier=self.credit_user_submission.credit.identifier)

    def test_get_is_blocked(self, **kwargs):
        super(UserCanEditSubmissionMixinTest, self).test_get_is_blocked(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id),
            category_abbreviation=(
                self.category_submission.category.abbreviation),
            subcategory_slug=self.subcategory_submission.subcategory.slug,
            credit_identifier=self.credit_user_submission.credit.identifier)
