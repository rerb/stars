from models import CreditSet, Category, Subcategory, Credit

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
    """
    comments = fields.ToManyField('stars.credits.api.resources.CommentResource', 'comments')
    
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
    """
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'credits/category'
        allowed_methods = ['get']
        
class SubcategoryResource(ModelResource):
    """
        Resource for accessing any Subcategory
    """
    class Meta:
        queryset = Subcategory.objects.all()
        resource_name = 'credits/subcategory'
        allowed_methods = ['get']
        
    