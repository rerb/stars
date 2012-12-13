"""Tests for apps.tool.views.
"""
import re

from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from mock import patch

import stars.apps.accounts.middleware as stars_middleware
from stars.apps.tests.views import ProtectedFormMixinViewTest, ViewTest
from stars.apps.tool.views import (NoStarsAccountView, ToolLandingPageView,
                                   SummaryToolView)
from stars.test_factories import (InstitutionFactory, StarsAccountFactory,
                                  UserFactory, UserProfileFactory)


class InstitutionToolMixinTest(ProtectedFormMixinViewTest):
    """
        Provides a base TestCase for views that inherit from
        InstitutionToolMixin.
    """
    blocked_user_level = None  # user_level that should be blocked
    blessed_user_level = None  # user_level that should be allowed to GET

    middleware = ProtectedFormMixinViewTest.middleware + [MessageMiddleware]

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


class SummaryToolViewTest(InstitutionViewOnlyToolMixinTest):
    """This test is included in the apps.tool.manage.tests test
    suite (e.g., it's included in __test__ in
    apps/tool/manage/tests/__init__.py).  That's the workaround for
    putting it up here, where it belongs, in apps/tool/views.py,
    even though there's no app called 'tool' -- putting it into
    the other test suite makes it easily runnable, e.g., as
    'manage.py test manage.SummaryToolViewTest'.
    """

    view_class = SummaryToolView

    def test_get_with_no_slug_raises_permission_denied(self):
        """Does a GET w/no institution slug raise a 403?"""
        with self.assertRaises(PermissionDenied):
            _ = self.view_class.as_view()(self.request,
                                          institution_slug='')


class ToolLandingPageViewTest(ViewTest):
    view_class = ToolLandingPageView

    def setUp(self):
        super(ToolLandingPageViewTest, self).setUp()
        self.request.user = UserFactory()

    def test_get_succeeds(self):
        """Is view.as_view() GET-able?
        """
        super(ToolLandingPageViewTest, self).test_get_succeeds(
            status_code=301)

    def test_redirect_when_no_stars_account(self):
        """Is the redirection when the user has no STARS accounts correct?"""
        with patch('stars.apps.tool.views.reverse') as reverse_mock:
            try:
                self.view_class.as_view()(request=self.request)
            except SuspiciousOperation:  # Django doesn't like reverse mocked.
                pass
            reverse_mock.assert_called_with('no-stars-account')

    def test_redirect_when_one_stars_account(self):
        """Is the redirection when the user has one STARS account correct?"""
        stars_account = StarsAccountFactory(user=self.request.user)
        with patch('stars.apps.tool.views.reverse') as reverse_mock:
            try:
                self.view_class.as_view()(request=self.request)
            except SuspiciousOperation:  # Django doesn't like reverse mocked.
                pass
            reverse_mock.assert_called_with('tool-summary',
                                            stars_account.institution.slug)

    def test_redirect_when_many_stars_accounts(self):
        """Is the redirection when the user has >1 STARS accounts correct?"""
        for i in (1, 2):
            _ = StarsAccountFactory(user=self.request.user)
        with patch('stars.apps.tool.views.reverse') as reverse_mock:
            try:
                self.view_class.as_view()(request=self.request)
            except SuspiciousOperation:  # Django doesn't like reverse mocked.
                pass
            reverse_mock.assert_called_with('select-institution')


class NoStarsAccountViewTest(ViewTest):

    view_class = NoStarsAccountView
    middleware = (ViewTest.middleware +
                  [AuthenticationMiddleware,
                   stars_middleware.AuthenticationMiddleware])

    def setUp(self):
        super(NoStarsAccountViewTest, self).setUp()
        self.user_profile = UserProfileFactory(profile_instlist='')
        self.request.user = self.user_profile.user
        self.view = self.view_class()

    def test_get_institution_empty_profile_instlist(self):
        self.assertEqual(self.view.get_institution(user=self.request.user),
                         None)

    def test_get_institution_one_valid_entry_profile_instlist(self):
        institution = InstitutionFactory()
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        self.assertEqual(self.view.get_institution(user=self.request.user),
                         institution)

    def test_get_institution_one_invalid_entry_profile_instlist(self):
        self.user_profile.profile_instlist = '-999'
        self.user_profile.save()
        self.assertEqual(self.view.get_institution(user=self.request.user),
                         None)

    def test_get_institution_two_valid_entries_profile_instlist(self):
        first_institution = InstitutionFactory()
        second_institution = InstitutionFactory()
        self.user_profile.profile_instlist = ','.join(
            (str(first_institution.id), str(second_institution.id)))
        self.user_profile.save()
        self.assertEqual(self.view.get_institution(user=self.request.user),
                         first_institution)

    def test_get_institution_two_invalid_entries_profile_instlist(self):
        self.user_profile.profile_instlist = '-999,-888'
        self.user_profile.save()
        self.assertEqual(self.view.get_institution(user=self.request.user),
                         None)

    def test_get_institution_one_valid_one_invalid_entries_profile_instlist(
            self):
        institution = InstitutionFactory()
        self.user_profile.profile_instlist = '-999,' + str(institution.id)
        self.user_profile.save()
        self.assertEqual(self.view.get_institution(user=self.request.user),
                         institution)

    def test_get_institution_one_participant_of_two_entries_profile_instlist(
            self):
        first_institution = InstitutionFactory()
        second_institution = InstitutionFactory(is_participant=True)
        self.user_profile.profile_instlist = ','.join(
            (str(first_institution.id), str(second_institution.id)))
        self.user_profile.save()
        self.assertEqual(self.view.get_institution(user=self.request.user),
                         second_institution)

    def test_get_institution_no_participant_of_two_entries_profile_instlist(
            self):
        first_institution = InstitutionFactory(is_participant=True)
        second_institution = InstitutionFactory(is_participant=True)
        self.user_profile.profile_instlist = ','.join(
            (str(first_institution.id), str(second_institution.id)))
        self.user_profile.save()
        self.assertEqual(self.view.get_institution(user=self.request.user),
                         first_institution)

    def test_get_liaison_name(self):
        institution = InstitutionFactory(
            contact_first_name='William',
            contact_middle_name='S',
            contact_last_name='Burroughs')
        self.assertEqual(self.view.get_liaison_name(institution),
                         'William S Burroughs')

    def test_get_liaison_name_no_middle_name(self):
        institution = InstitutionFactory(
            contact_first_name='William',
            contact_last_name='Burroughs')
        self.assertEqual(self.view.get_liaison_name(institution),
                         'William Burroughs')

    def test_get_liaison_phone_no_extension(self):
        institution = InstitutionFactory(contact_phone='8675309')
        self.assertEqual(self.view.get_liaison_phone(institution),
                         '8675309')

    def test_get_liaison_phone_with_extension(self):
        institution = InstitutionFactory(contact_phone='8675309',
                                         contact_phone_ext='9')
        self.assertEqual(self.view.get_liaison_phone(institution),
                         '8675309 x9')

    def test_liaison_name_shown(self):
        institution = InstitutionFactory(is_participant=True,
                                         contact_first_name='Joan')
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        response = self.view_class.as_view()(request=self.request)
        self.assertTrue(re.search(',\s*Joan,\s*can grant you',
                                  response.rendered_content))

    def test_no_liaison_name_shown(self):
        institution = InstitutionFactory(name='Grantland State',
                                         is_participant=True)
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        response = self.view_class.as_view()(request=self.request)
        self.assertTrue(re.search('Grantland State\s*can grant you',
                                  response.rendered_content))

    def test_liaison_phone_shown(self):
        institution = InstitutionFactory(name='Grantland State',
                                         is_participant=True,
                                         contact_phone='4561234')
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        response = self.view_class.as_view()(request=self.request)
        self.assertTrue(re.search('by phone at 4561234.',
                                  response.rendered_content))

    def test_no_liaison_phone_shown(self):
        institution = InstitutionFactory(is_participant=True)
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        response = self.view_class.as_view()(request=self.request)
        self.assertFalse(re.search('by phone at',
                                   response.rendered_content))

    def test_liaison_email_shown(self):
        institution = InstitutionFactory(is_participant=True,
                                         contact_email='j@b.c')
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        response = self.view_class.as_view()(request=self.request)
        self.assertTrue(re.search('by email at j@b.c.',
                                  response.rendered_content))

    def test_no_liaison_email_shown(self):
        institution = InstitutionFactory(is_participant=True)
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        response = self.view_class.as_view()(request=self.request)
        self.assertFalse(re.search('by email at',
                                   response.rendered_content))

    def test_liaison_phone_and_email_shown(self):
        institution = InstitutionFactory(is_participant=True,
                                         contact_phone='4561234',
                                         contact_email='j@b.c')
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        response = self.view_class.as_view()(request=self.request)
        self.assertTrue(re.search(
            'by phone at 4561234\s*and by email at j@b.c.',
            response.rendered_content))

    def test_no_institution_name_shown(self):
        institution = InstitutionFactory(name='Bully For U',
                                         is_participant=True)
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        response = self.view_class.as_view()(request=self.request)
        self.assertTrue(re.search('Bully For U', response.rendered_content))

    def test_institution_is_participant_shown(self):
        institution = InstitutionFactory(is_participant=True)
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        response = self.view_class.as_view()(request=self.request)
        self.assertTrue(re.search('The STARS Liaison for',
                                  response.rendered_content))

    def test_institution_is_not_participant_shown(self):
        institution = InstitutionFactory(is_participant=False)
        self.user_profile.profile_instlist = str(institution.id)
        self.user_profile.save()
        response = self.view_class.as_view()(request=self.request)
        self.assertTrue(re.search("isn't currently registered as a STARS",
                                  response.rendered_content))
