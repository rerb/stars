"""
    STARS Institutions API
"""
from tastypie import fields

from stars.apps.institutions import models
from stars.apps.submissions.models import SubmissionSet
from stars.apps.api.resources import StarsApiResource
from stars.apps.api.paths import SUBMISSIONS_RESOURCE_PATH


class InstitutionResource(StarsApiResource):
    """
        Resource for accessing any Institution.
    """
    submission_sets = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + "NestedSubmissionSetResource",
        'submissionset_set', full=True)

    class Meta(StarsApiResource.Meta):
        queryset = models.Institution.objects.filter(enabled=True)
        resource_name = 'institutions'
        # @todo: need aashe_id and/or id?
        fields = ['name', 'aashe_id', 'id']
        allowed_methods = ['get']

    def dehydrate_submission_sets(self, bundle):
        """Filter unrated submission sets."""
        for submission in bundle.data['submission_sets']:
            if submission not in SubmissionSet.objects.get_rated():
                del(submission)
        return bundle.data['submission_sets']


class NestedInstitutionResource(StarsApiResource):
    """
        A resource for embedding institution info in other resources.
        A middle way between just an InstitutionResource URI and full=True.
    """
    class Meta(InstitutionResource.Meta):
        fields = ['name']
        allowed_methods = []
