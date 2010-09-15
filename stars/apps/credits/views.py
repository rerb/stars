import sys

from django.shortcuts import get_object_or_404
from django.http import Http404

from stars.apps.helpers.forms.views import TemplateView
from stars.apps.credits.models import *


class CreditNavMixin(TemplateView):
    """
        Class-based mix-in view that can

            - extract the Category, Subcategory, and Credit
              from the variables passed to __call__()

            - provide the outline for the left nav menu for the CreditSet

        Thoughts:

            - use a `get_context_from_request` method so that it can be used with mixins
    """
        
    def get_creditset_selection(self, request, creditset, **kwargs):
        """
            Gets the Category/Subcategory/Credit from the kwargs
            returns a tuple: (category, subcategory, credit)
            assumes the naming scheme: category_id/subcategory_id/credit_id
        """
        
        category = None
        subcategory = None
        credit = None
        
        # Get the CategorySubmission
        if kwargs.has_key('category_id'):
            category = get_object_or_404(Category, id=kwargs['category_id'], creditset=creditset)
            
            # Get the SubcategorySubmission
            if kwargs.has_key('subcategory_id'):
                subcategory = get_object_or_404(Subcategory, id=kwargs['subcategory_id'], category=category)
                
                # Get the Credit
                if kwargs.has_key('credit_id'):
                    credit = get_object_or_404(Credit, id=kwargs['credit_id'], subcategory=subcategory)
                    
        return (category, subcategory, credit)
        
    def get_creditset_navigation(self, creditset, url_prefix=None, current=None):
        """
            Provides a list of categories for a given `creditset`,
            each with a subcategory dict containing a list of subcategories,
            each with credits and tier2 credits dicts containing lists of credits
            
            Category:
                {'title': title, 'url': url, 'subcategories': subcategory_list}
            Subcategory:
                {'title': title, 'url': url, 'credits': credit_list, 'tier2': credit_list}
            Credit:
                {'title': title, 'url': url}
        """
        outline = []
        # Top Level: Categories
        for cat in creditset.category_set.all():
            
            subcategories = []
            
            # Second Level: Subcategories
            for sub in cat.subcategory_set.all():
                credits = []
                tier2 = []
                
                # Third Level: Credits
                for credit in sub.credit_set.all():
                    c = {
                            'title': credit.__unicode__(),
                            'url': self.get_credit_url(credit, url_prefix),
                            'id': credit.id,
                            'selected': False,
                        }
                    if current == credit:
                        c['selected'] = True
                    if credit.type == 't1':
                        credits.append(c)
                    elif credit.type == 't2':
                        tier2.append(c)
                
                temp_sc =   {
                            'title': sub.title,
                            'url': self.get_subcategory_url(sub, url_prefix),
                            'credits': credits,
                            'tier2': tier2,
                            'id': sub.id,
                            'selected': False,
                        }
                if current == sub:
                    temp_sc['selected'] = True
                    
                subcategories.append(temp_sc)
                             
            temp_c =    {
                            'title': cat.title,
                            'url': self.get_category_url(cat, url_prefix),
                            'subcategories': subcategories,
                            'id': cat.id,
                            'selected': False,
                        }
            if current == cat:
                temp_c['selected'] = True
            outline.append(temp_c)
        
        return outline
        
    def get_category_url(self, category, url_prefix=None):
        """ The default link for a category. """
        raise NotImplementedError, "Your inheriting class needs to define this"
        
    def get_subcategory_url(self, subcategory, url_prefix=None):
        """ The default link for a category. """
        raise NotImplementedError, "Your inheriting class needs to define this"
        
    def get_credit_url(self, credit, url_prefix=None):
        """ The default credit link. """
        raise NotImplementedError, "Your inheriting class needs to define this"
