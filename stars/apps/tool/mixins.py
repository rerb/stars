from stars.apps.accounts.mixins import StarsAccountMixin
from aashe_rules.mixins import RulesMixin
from stars.apps.submissions.views import SubmissionStructureMixin

class ToolMixin(StarsAccountMixin, RulesMixin, SubmissionStructureMixin):
    
    def get_success_url(self):
        """
            Forms almost always stay on the page they were
        """
        return self.request.path