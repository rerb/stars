from django.core.urlresolvers import reverse

from aashe_rules.mixins import RulesMixin
from stars.apps.accounts.mixins import StarsAccountMixin
from stars.apps.institutions.views import InstitutionStructureMixin
from stars.apps.submissions.views import SubmissionStructureMixin


class ToolMixin(RulesMixin, StarsAccountMixin):

    def get_success_url(self, institution_slug=None):
        """
            Forms redirect to the named url specified as
            success_url_name, the url specified as success_url,
            or stay on the same page.
        """
        if getattr(self, 'success_url_name', False):
            institution_slug = (institution_slug or
                                self.kwargs['institution_slug'])
            return reverse(self.success_url_name,
                           kwargs={'institution_slug': institution_slug})
        elif getattr(self, 'success_url', False):
            return self.success_url
        else:
            return self.request.path

    def get_context_data(self, **kwargs):
        """
            If this ToolMixin has an attribute named 'tab_content_title',
            pass it along in the form context.
        """
        context = super(ToolMixin, self).get_context_data(**kwargs)
        try:
            context['tab_content_title'] = self.get_tab_content_title()
        except AttributeError:
            pass
        return context

    def get_tab_content_title(self):
        """
            Returns self.tab_content_title.  Provides a hook for
            subclasses to deduce tab_content_title programmatically.
        """
        return self.tab_content_title


class InstitutionToolMixin(ToolMixin, InstitutionStructureMixin):
    """
        A ToolMixin with knowledge of the Institution structure.
    """
    pass


class InstitutionAdminToolMixin(InstitutionToolMixin):
    """
        An InstitutionToolMixin that's available only to institution admins.
    """
    def update_logical_rules(self):
        super(InstitutionAdminToolMixin, self).update_logical_rules()
        self.add_logical_rule({ 'name': 'user_is_institution_admin',
                                'param_callbacks': [
                                    ('user', 'get_request_user'),
                                    ('institution', 'get_institution')] })


class SubmissionToolMixin(InstitutionToolMixin,
                          SubmissionStructureMixin):
    """
        An InstitutionToolMixin with knowledge of the Submission structure.
    """
    pass


class UserCanEditSubmissionMixin(SubmissionToolMixin):
    """
        A SubmissionToolMixin that's available only to users with
        permission to edit submissions.
    """
    def update_logical_rules(self):
        super(UserCanEditSubmissionMixin, self).update_logical_rules()
        self.add_logical_rule({ 'name': 'user_can_edit_submission',
                                'param_callbacks': [
                                    ('user', 'get_request_user'),
                                    ('submission', 'get_submissionset')] })


class SubmissionSetIsNotLockedMixin(SubmissionToolMixin):
    """
        A SubmissionToolMixin that's available only if the current
        submissionset is not locked.
    """
    def update_logical_rules(self):
        super(SubmissionSetIsNotLockedMixin, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'submission_is_not_locked',
            'param_callbacks': [('submission', 'get_submissionset')],
            'redirect_url': reverse('submission-locked') })
