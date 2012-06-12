from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

import stars.apps.credits.models as credits_models


"""
    STARS Credit API

    @todo:
        - authentication
        - authorization
        - dehydration
"""

BASE_RESOURCE_PATH = 'stars.apps.credits.api.resources.'


class JSONForHTMLSerializer(Serializer):
    """
        Serializer that returns JSON when asked for HTML.  Removes
        requirement for requests from web browsers to specify a
        format.
    """

    def to_html(self, data, options):
        return self.to_json(data, options)


class StarsApiResource(ModelResource):

    class Meta:
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        serializer = JSONForHTMLSerializer()


class CategoryResource(StarsApiResource):
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

    class Meta(StarsApiResource.Meta):
        queryset = credits_models.Category.objects.all()
        resource_name = 'credits/category'
        allowed_methods = ['get']


class CreditResource(StarsApiResource):
    """
        Resource for accessing any Credit
    """
    subcategory = fields.ForeignKey(BASE_RESOURCE_PATH + 'SubcategoryResource',
                                    'subcategory')

    class Meta(StarsApiResource.Meta):
        queryset = credits_models.Credit.objects.all()
        resource_name = 'credits/credit'
        allowed_methods = ['get']
        # exclude these fields because they raise
        # "'ascii' codec can't decode byte ... in position ...: ordinal not
        # in range(128)"
        excludes = ['validation_rules',
                    'criteria',
                    'scoring']


class CreditSetResource(StarsApiResource):
    """
        Resource for accessing any CreditSet
    """
    categories = fields.ManyToManyField(
        BASE_RESOURCE_PATH + 'CategoryResource',
        'category_set', related_name='creditset')

    class Meta(StarsApiResource.Meta):
        queryset = credits_models.CreditSet.objects.all()
        resource_name = 'credits/creditset'
        fields = ['id', 'release_date', 'version', 'supported_features']
        allowed_methods = ['get']


class DocumentationFieldResource(StarsApiResource):
    """
        Resource for accessing any DocumentationField
    """
    credit = fields.ForeignKey(BASE_RESOURCE_PATH + 'CreditResource', 'credit')

    class Meta(StarsApiResource.Meta):
        queryset = credits_models.DocumentationField.objects.all()
        resource_name = 'credits/field'
        allowed_methods = ['get']


class SubcategoryResource(StarsApiResource):
    """
        Resource for accessing any Subcategory
    """
    category = fields.ForeignKey(BASE_RESOURCE_PATH + 'CategoryResource',
                                 'category')

    class Meta(StarsApiResource.Meta):
        queryset = credits_models.Subcategory.objects.all()
        resource_name = 'credits/subcategory'
        allowed_methods = ['get']
