"""Tests for apps.tool.views.
"""
from django.contrib.messages.middleware import MessageMiddleware

from stars.apps.tests.views import ProtectedViewTest
from stars.apps.tool.views import SummaryToolView
from stars.test_factories import InstitutionFactory, StarsAccountFactory


class InstitutionToolMixinTest(ProtectedViewTest):
    """
        Provides a base TestCase for views that inherit from
        InstitutionToolMixin.
    """
    blocked_user_level = None  # user_level that should be blocked
    blessed_user_level = None  # user_level that should be allowed to GET

    middleware = ProtectedViewTest.middleware + [MessageMiddleware]

    def setUp(self):
        super(InstitutionToolMixinTest, self).setUp()
        self.institution = InstitutionFactory(slug='on-the-beach-soldier')
        self.account = StarsAccountFactory(institution=self.institution)
        self.request.user = self.account.user

    def open_gate(self):
        self._assign_user_level(self.blessed_user_level)

    def close_gate(self):
        self._assign_user_level(self.blocked_user_level)

    def _assign_user_level(self, user_level):
        self.account.user_level = user_level
        self.account.save()

    def _get_pk(self):
        """
            Provides the value for the kwarg named 'pk' that's
            passed to the view's on_view() product.
        """
        return ''

    def test_success_url_is_loadable(self, **kwargs):
        super(InstitutionToolMixinTest, self).test_get_succeeds(
            institution_slug=self.institution.slug,
            pk=self._get_pk())

    def test_get_succeeds(self):
        super(InstitutionToolMixinTest, self).test_get_succeeds(
            institution_slug=self.institution.slug,
            pk=self._get_pk())

    def test_get_is_blocked(self):
        super(InstitutionToolMixinTest, self).test_get_is_blocked(
            institution_slug=self.institution.slug,
            pk=self._get_pk())


class InstitutionAdminToolMixinTest(InstitutionToolMixinTest):
    """
        Provides a base TestCase for InstitutionToolMixinTests that
        are protected; only admin users can GET them.
    """
    view_class = None  # Must be set in subclass.
    blocked_user_level = ''
    blessed_user_level = 'admin'


class InstitutionViewOnlyToolMixinTest(InstitutionToolMixinTest):
    """
       Base class for InstitutionToolMixin views that are accessible
       by users with at least 'view' access for the institution.
    """
    blessed_user_level = 'view'
    blocked_user_level = ''
