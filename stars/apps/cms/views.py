from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect

from stars.apps.cms.models import *
from stars.apps.helpers.views import TemplateView


class CMSView(TemplateView):
    """ A base context for all CMS views """

    @property
    def __name__(self):
        return self.__class__.__name__

    def get_context(self, request, *args, **kwargs):
        """ Add/update any context variables """

        # Creating inital values for each of these so that
        # I can use them as cache keys in the template
        _context = {'category': None, 'subcategory': None, 'article': None}

        if kwargs.has_key('category_slug'):
            try:
                category = Category.objects.get(slug=kwargs['category_slug'], published=True)
            except Category.DoesNotExist:
                try:
                    subcategory = Subcategory.objects.get(slug=kwargs['category_slug'], published=True)
                    return HttpResponseRedirect(subcategory.get_absolute_url())
                except Subcategory.DoesNotExist:
                    raise Http404

            _context['category'] = category

            if kwargs.has_key('subcategory_slug'):
                subcategory = get_object_or_404(Subcategory, slug=kwargs['subcategory_slug'], parent=category, published=True)
                _context['subcategory'] = subcategory
            else:
                subcategory = None

            if kwargs.has_key('article_slug'):
                article = get_object_or_404(NewArticle, slug=kwargs['article_slug'], published=True)
                if category not in article.categories.all() and subcategory not in article.subcategories.all():
                    raise Http404
                _context['article'] = article

        return _context

category_detail = CMSView(template='cms/category_detail.html')
subcategory_detail = CMSView(template='cms/subcategory_detail.html')
article_detail = CMSView(template='cms/article_detail.html')

def old_path(request, category_slug, nid):
    """
        Forwards from the old link system.
    """
    article = get_object_or_404(NewArticle, irc_id=nid, published=True)
    return HttpResponseRedirect(article.get_absolute_url())
