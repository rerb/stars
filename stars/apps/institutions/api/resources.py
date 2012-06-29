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
        SUBMISSIONS_RESOURCE_PATH + "SubmissionSetResource",
        'submissionset_set')

    class Meta(StarsApiResource.Meta):
        # @todo: filter out Institutions w/enabled == False?
        queryset = models.Institution.objects.all()
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
