from django.core.urlresolvers import reverse

from aashe_rules.mixins import RulesMixin
from stars.apps.accounts.mixins import StarsAccountMixin
from stars.apps.institutions.views import InstitutionStructureMixin
from stars.apps.submissions.views import SubmissionStructureMixin


class ToolMixin(StarsAccountMixin, RulesMixin, SubmissionStructureMixin):

    def get_success_url(self, institution_slug=None):
        """
            Forms redirect to the named url specified as
            success_url_name, or stay on the same page.
        """
        if getattr(self, 'success_url_name', False):
            institution_slug = (institution_slug or
                                self.kwargs['institution_slug'])
            return reverse(self.success_url_name,
                           kwargs={'institution_slug': institution_slug})
        else:
            return self.request.path


class AdminToolMixin(ToolMixin, InstitutionStructureMixin):
    """
        A ToolMixin that's available only to institution admins.
    """
    logical_rules = [{'name': 'user_is_institution_admin',
                      'param_callbacks': [('user', 'get_request_user'),
                                          ('institution', 'get_institution')]}]
