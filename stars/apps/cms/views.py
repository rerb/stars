from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.views.generic.base import RedirectView, TemplateView

from stars.apps.cms.models import Category, NewArticle, Subcategory


class CMSView(TemplateView):
    """
        A base context for all CMS views
    """
    def get_context_data(self, *args, **kwargs):
        """ Add/update any context variables """

        # Creating inital values for each of these so that
        # I can use them as cache keys in the template
        _context = {'category': None, 'subcategory': None, 'article': None}

        if kwargs.has_key('category_slug'):
            try:
                category = Category.objects.get(slug=kwargs['category_slug'],
                                                published=True)
            except Category.DoesNotExist:
                try:
                    subcategory = Subcategory.objects.get(
                        slug=kwargs['category_slug'], published=True)
                    return HttpResponseRedirect(subcategory.get_absolute_url())
                except Subcategory.DoesNotExist:
                    raise Http404

            _context['category'] = category

            if kwargs.has_key('subcategory_slug'):
                subcategory = get_object_or_404(Subcategory,
                                                slug=kwargs['subcategory_slug'],
                                                parent=category, published=True)
                _context['subcategory'] = subcategory
            else:
                subcategory = None

            if kwargs.has_key('article_slug'):
                article = get_object_or_404(NewArticle,
                                            slug=kwargs['article_slug'],
                                            published=True)
                if (category not in article.categories.all() and
                    subcategory not in article.subcategories.all()):
                    raise Http404
                _context['article'] = article

        return _context


class ArticleDetailView(CMSView):
    """
        Detail page for one CMS article.
    """
    template_name = 'cms/article_detail.html'


class CategoryDetailView(CMSView):
    """
        Detail page for a CMS category.
    """
    template_name = 'cms/category_detail.html'


class SubcategoryDetailView(CMSView):
    """
        Detail page for a CMS subcategory.
    """
    template_name = 'cms/subcategory_detail.html'


class OldPathRedirectView(RedirectView):
    """
        Redirects article URLs from the old link system.
    """
    def get_redirect_url(self, nid):
        article = get_object_or_404(NewArticle, irc_id=nid, published=True)
        return article.get_absolute_url()
