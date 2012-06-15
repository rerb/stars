from tastypie import fields

import stars.apps.submissions.models as submissions_models
from stars.apps.api.resources import StarsApiResource

"""
    STARS Submissions API
"""

BASE_RESOURCE_PATH = 'stars.apps.submissions.newapi.resources.'
CREDITS_RESOURCE_PATH = 'stars.apps.credits.api.resources.'

# /submissions/ - list of all submission sets (per auth)
# /submissions/<id>/ - specific submission set
# /submissions/category/
# /submissions/category/<id>/
# /submissions/subcategory/
# /submissions/subcategory/<id>/
# /submissions/credit/
# /submissions/credit/<id>/
# /submissions/field/
# /submissions/field/<id>/


class SubmissionSetResource(StarsApiResource):
    """
    creditset = models.ForeignKey(CreditSet)
    institution = models.ForeignKey(Institution)
    rating = models.ForeignKey(Rating, blank=True, null=True)
    """
    categories = fields.OneToManyField(
        BASE_RESOURCE_PATH + 'CategorySubmissionResource',
        'categorysubmission_set')
    creditset = fields.OneToOneField(
        CREDITS_RESOURCE_PATH + 'CreditSetResource', 'creditset')

    class Meta(StarsApiResource.Meta):
        # queryset = submissions_models.SubmissionSet.objects.published()
        queryset = submissions_models.SubmissionSet.objects.all()
        resource_name = 'submissions/submissionset'
        allowed_methods = ['get']
        # exclude submission_boundary becauses it raises
        # "'ascii' codec can't decode byte ... in position ...: ordinal not
        # in range(128)"
        excludes = ['submission_boundary',]


class CategorySubmissionResource(StarsApiResource):
    """
        Resource for accessing any CategorySubmission
    """
    subcategories = fields.OneToManyField(
        BASE_RESOURCE_PATH + 'SubcategorySubmissionResource',
        'subcategorysubmission_set', related_name='category')
    category = fields.OneToOneField(
        CREDITS_RESOURCE_PATH + 'CategoryResource', 'category')

    class Meta(StarsApiResource.Meta):
        queryset = submissions_models.CategorySubmission.objects.all()
        resource_name = 'submissions/category'
        allowed_methods = ['get']


class SubcategorySubmissionResource(StarsApiResource):
    """
        Resource for accessing any SubcategorySubmission
    """
    # category = fields.ForeignKey(
    #     BASE_RESOURCE_PATH + 'CategorySubmissionResource', 'category')

    class Meta(StarsApiResource.Meta):
        queryset = submissions_models.SubcategorySubmission.objects.all()
        resource_name = 'submissions/subcategory'
        allowed_methods = ['get']

class CreditSubmissionResource(StarsApiResource):
    """
        Resource for accessing any CreditSubmission
    """
    # category = fields.ForeignKey(
    #     BASE_RESOURCE_PATH + 'CategorySubmissionResource', 'category')

    class Meta(StarsApiResource.Meta):
        queryset = submissions_models.CreditUserSubmission.objects.all()
        resource_name = 'submissions/credit'
        allowed_methods = ['get']

# class DocumentationFieldSubmissionResource(StarsApiResource):
#     """
#         Resource for accessing any DocumentationFieldSubmission
#     """
#     # category = fields.ForeignKey(
#     #     BASE_RESOURCE_PATH + 'CategorySubmissionResource', 'category')

#     class Meta(StarsApiResource.Meta):
#         queryset = submissions_models.DocumentationFieldSubmission.objects.all()
#         resource_name = 'submissions/field'
#         allowed_methods = ['get']

        # class CreditResource(StarsApiResource):
#     """
#         Resource for accessing any Credit
#     """
#     subcategory = fields.ForeignKey(BASE_RESOURCE_PATH + 'SubcategoryResource',
#                                     'subcategory')

#     class Meta(StarsApiResource.Meta):
#         queryset = credits_models.Credit.objects.all()
#         resource_name = 'credits/credit'
#         allowed_methods = ['get']
#         # exclude these fields because they raise
#         # "'ascii' codec can't decode byte ... in position ...: ordinal not
#         # in range(128)"
#         excludes = ['validation_rules',
#                     'criteria',
#                     'scoring']


# class CreditSetResource(StarsApiResource):
#     """
#         Resource for accessing any CreditSet
#     """
#     categories = fields.ManyToManyField(
#         BASE_RESOURCE_PATH + 'CategoryResource',
#         'category_set', related_name='creditset')

#     class Meta(StarsApiResource.Meta):
#         queryset = credits_models.CreditSet.objects.all()
#         resource_name = 'credits/creditset'
#         fields = ['id', 'release_date', 'version', 'supported_features']
#         allowed_methods = ['get']


# class DocumentationFieldResource(StarsApiResource):
#     """
#         Resource for accessing any DocumentationField
#     """
#     credit = fields.ForeignKey(BASE_RESOURCE_PATH + 'CreditResource', 'credit')

#     class Meta(StarsApiResource.Meta):
#         queryset = credits_models.DocumentationField.objects.all()
#         resource_name = 'credits/field'
#         allowed_methods = ['get']
