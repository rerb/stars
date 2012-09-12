from stars.apps.institutions.models import Institution
from stars.apps.credits.mixins import CreditsetStructureMixin

from django.shortcuts import get_object_or_404

class SubmissionStructureMixin(CreditsetStructureMixin):
    """
        Retrieves objects from the URL kwargs for a Submission
    """

    def get_institution(self, refresh=False):
        """
            Get's the selected institution from the URL
        """
        i = self.get_structure_object('current_inst')
        if not i or refresh:
            i = get_object_or_404(Institution, slug=self.kwargs['institution_slug'])
            self.set_structure_object('current_inst', i)
        return i
