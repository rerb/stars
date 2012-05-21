from stars.apps.credits.models import CreditSet, Category, Subcategory, Credit

from tastypie import fields
from tastypie.resources import ModelResource, Resource
from tastypie.bundle import Bundle
from tastypie.cache import SimpleCache

from django.core.urlresolvers import reverse
from django.core.cache import cache

"""
    STARS Credit API
    
    @todo:
        - authentication
        - authorization
        - dehydration
"""

class CreditSetResource(ModelResource):
    """
        Resource for accessing any CreditSet
        
        @todo: this needs a list of categories
        
        class EntryResource(ModelResource):
            authors = fields.ToManyField('path.to.api.resources.AuthorResource', 'author_set', related_name='entry')
    """
    categories = fields.ToManyField('stars.apps.credits.api.resources.CategoryResource', 'category_set', related_name='creditset')
    
    class Meta:
        queryset = CreditSet.objects.all()
        resource_name = 'credits/creditset'
        fields = ['id', 'release_date', 'version']
        allowed_methods = ['get']
        
class CategoryResource(ModelResource):
    """
        Resource for accessing any Category
        
        Note: I had thought about using more structured URLS
        but I think this might be simpler...??
        
        class AuthorResource(ModelResource):
            entry = fields.ToOneField(EntryResource, 'entry')
    """
    creditset = fields.ToOneField(CreditSetResource, 'creditset')
    subcategories = fields.ToManyField('stars.apps.credits.api.resources.SubcategoryResource', 'subcategory_set', related_name='category')
    
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'credits/category'
        allowed_methods = ['get']
        
class SubcategoryResource(ModelResource):
    """
        Resource for accessing any Subcategory
    """
    category = fields.ToOneField(CategoryResource, 'category')
    
    class Meta:
        queryset = Subcategory.objects.all()
        resource_name = 'credits/subcategory'
        allowed_methods = ['get']