"""
    STARS Credit API

    @todo:
        - authentication
        - authorization
        - dehydration
"""
from tastypie import fields

import stars.apps.credits.models as credits_models
from stars.apps.api.resources import StarsApiResource
from stars.apps.api.paths import CREDITS_RESOURCE_PATH

class CategoryResource(StarsApiResource):
    """
        Resource for accessing any Category

        Note: I had thought about using more structured URLS
        but I think this might be simpler...??

        class AuthorResource(ModelResource):
            entry = fields.ForeignKey(EntryResource, 'entry')
    """
    creditset = fields.ForeignKey(CREDITS_RESOURCE_PATH + 'CreditSetResource',
                                  'creditset')
    subcategories = fields.OneToManyField(
        CREDITS_RESOURCE_PATH + 'SubcategoryResource', 'subcategory_set',
        related_name='category')

    class Meta(StarsApiResource.Meta):
        queryset = credits_models.Category.objects.all()
        resource_name = 'credits/category'
        allowed_methods = ['get']
        excludes = ['max_point_value']


class NestedCategoryResource(StarsApiResource):
    """
        A resource for nesting Category info in other resources.
        Shows fewer fields, disallows all HTTP methods.
    """
    class Meta(CategoryResource.Meta):
        fields = ['title', 'resource_uri']
        allowed_methods = None


class CreditResource(StarsApiResource):
    """
        Resource for accessing any Credit
    """
    subcategory = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'SubcategoryResource',
        'subcategory')
    documentation_fields = fields.ManyToManyField(
        CREDITS_RESOURCE_PATH + 'DocumentationFieldResource',
        'documentationfield_set', related_name='credit')

    class Meta(StarsApiResource.Meta):
        queryset = credits_models.Credit.objects.all()
        resource_name = 'credits/credit'
        allowed_methods = ['get']
        # exclude these fields because they raise
        # "'ascii' codec can't decode byte ... in position ...: ordinal not
        # in range(128)"
        excludes = ['validation_rules',
                    'formula',
                    'staff_notes'
                   ]


class CreditSetResource(StarsApiResource):
    """
        Resource for accessing any CreditSet
    """
    categories = fields.ManyToManyField(
        CREDITS_RESOURCE_PATH + 'NestedCategoryResource',
        'category_set', related_name='creditset', full=True)

    class Meta(StarsApiResource.Meta):
        queryset = credits_models.CreditSet.objects.filter(version__gte='1.0')
        resource_name = 'credits/creditset'
        fields = ['id', 'release_date', 'version', 'supported_features']
        allowed_methods = ['get']


class NestedCreditSetResource(StarsApiResource):
    """
        An abbreviated CreditSetResource for embedding within other
        resources.
    """
    class Meta(CreditSetResource.Meta):
        fields = ['version']
        allowed_methods = None


class DocumentationFieldResource(StarsApiResource):
    """
        Resource for accessing any DocumentationField
    """
    credit = fields.ForeignKey(CREDITS_RESOURCE_PATH + 'CreditResource',
                               'credit')

    class Meta(StarsApiResource.Meta):
        queryset = credits_models.DocumentationField.objects.all()
        resource_name = 'credits/field'
        allowed_methods = ['get']
        excludes = [
                    'last_choice_is_other',
                    'is_published',
                    'identifier',
                ]


class SubcategoryResource(StarsApiResource):
    """
        Resource for accessing any Subcategory
    """
    category = fields.ForeignKey(CREDITS_RESOURCE_PATH + 'CategoryResource',
                                 'category')
    credits = fields.OneToManyField(
        CREDITS_RESOURCE_PATH + 'CreditResource', 'credit_set',
        related_name='subcategory')

    class Meta(StarsApiResource.Meta):
        queryset = credits_models.Subcategory.objects.all()
        resource_name = 'credits/subcategory'
        allowed_methods = ['get']
        excludes = ['max_point_value']
