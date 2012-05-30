from stars.apps.credits.models import *

from tastypie import fields
from tastypie.resources import ModelResource

"""
    STARS Credit API

    @todo:
        - authentication
        - authorization
        - dehydration
"""

BASE_RESOURCE_PATH = 'stars.apps.credits.api.resources.'


class CategoryResource(ModelResource):
    """
        Resource for accessing any Category

        Note: I had thought about using more structured URLS
        but I think this might be simpler...??

        class AuthorResource(ModelResource):
            entry = fields.ForeignKey(EntryResource, 'entry')
    """
    creditset = fields.ForeignKey(BASE_RESOURCE_PATH + 'CreditSetResource',
                                  'creditset')
    subcategories = fields.OneToManyField(
        BASE_RESOURCE_PATH + 'SubcategoryResource', 'subcategory_set',
        related_name='category')

    class Meta:
        queryset = Category.objects.all()
        resource_name = 'credits/category'
        allowed_methods = ['get']


class CreditResource(ModelResource):
    """
        Resource for accessing any Credit
    """
    subcategory = fields.ForeignKey(BASE_RESOURCE_PATH + 'SubcategoryResource',
                                    'subcategory')

    class Meta:
        queryset = Credit.objects.all()
        resource_name = 'credits/credit'
        allowed_methods = ['get']
        # exclude these fields because they raise
        # "'ascii' codec can't decode byte ... in position ...: ordinal not
        # in range(128)"
        excludes = ['validation_rules',
                    'criteria',
                    'scoring']


class CreditSetResource(ModelResource):
    """
        Resource for accessing any CreditSet
    """
    categories = fields.ManyToManyField(
        BASE_RESOURCE_PATH + 'CategoryResource',
        'category_set', related_name='creditset')
    supported_features = fields.OneToManyField(
        BASE_RESOURCE_PATH + 'IncrementalFeatureResource',
        'supported_features', related_name='creditsets')

    class Meta:
        queryset = CreditSet.objects.all()
        resource_name = 'credits/creditset'
        fields = ['id', 'release_date', 'version', 'supported_features']
        allowed_methods = ['get']


class DocumentationFieldResource(ModelResource):
    """
        Resource for accessing any DocumentationField
    """
    credit = fields.ForeignKey(BASE_RESOURCE_PATH + 'CreditResource', 'credit')

    class Meta:
        queryset = DocumentationField.objects.all()
        resource_name = 'credits/documentationfield'
        allowed_methods = ['get']


class IncrementalFeatureResource(ModelResource):
    """
        Resource for accessing any IncrementalFeature
    """
    creditsets = fields.ManyToManyField(
        BASE_RESOURCE_PATH + 'CreditSetResource',
        'creditset_set')

    class Meta:
        queryset = IncrementalFeature.objects.all()
        resource_name = 'credits/incrementalfeature'
        allowed_methods = ['get']


class SubcategoryResource(ModelResource):
    """
        Resource for accessing any Subcategory
    """
    category = fields.ForeignKey(BASE_RESOURCE_PATH + 'CategoryResource',
                                 'category')

    class Meta:
        queryset = Subcategory.objects.all()
        resource_name = 'credits/subcategory'
        allowed_methods = ['get']
