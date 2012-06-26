"""
    STARS Institutions API
"""
from tastypie import fields

from stars.apps.institutions import models
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
