from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.views.generic.base import RedirectView, TemplateView

from stars.apps.old_cms.models import Category, NewArticle, Subcategory

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, *args, **kwargs):
        """ Add/update any context variables """

        context = super(HomePageView, self).get_context_data(*args, **kwargs)

        context['categories'] = Category.objects.filter(published=True).order_by('ordinal')

        return context


class CMSView(TemplateView):
    """
        A base context for all CMS views
    """
    def __init__(self, *args, **kwargs):
        super(CMSView, self).__init__(*args, **kwargs)
        self.category = None  # so we can suss category in get() and
                              # access it in get_context_data()

    def _get_slugged_obj(self, slug):
        """Returns the Category or Subcategory whose slug matches `slug`.

        Returns None if `slug` doesn't match any Category or Subcategory.
        """
        try:
            obj = Category.objects.get(slug=slug, published=True)
        except Category.DoesNotExist:
            try:
                obj = Subcategory.objects.get(slug=slug, published=True)
            except Subcategory.DoesNotExist:
                obj = None
        return obj

    def get(self, request, *args, **kwargs):
        """
        kwargs['category_slug'] can specify a Category.slug or a
        Subcategory.slug.  If it doesn't match a Category.slug, but
        does match a Subcategory.slug, we redirect to the Subcategory
        URL.
        """
        slugged_obj = self._get_slugged_obj(slug=kwargs['category_slug'])
        if isinstance(slugged_obj, Category):
            self.category = slugged_obj
        elif isinstance(slugged_obj, Subcategory):
            return HttpResponseRedirect(slugged_obj.get_absolute_url())
        else:
            raise Http404

        return super(CMSView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """ Add/update any context variables """

        context = super(CMSView, self).get_context_data(*args, **kwargs)

        context['categories'] = Category.objects.filter(published=True).order_by('ordinal')

        # Creating inital values for each of these so that
        # I can use them as cache keys in the template
        context.update({'category': self.category,
                        'subcategory': None,
                        'article': None})

        if 'subcategory_slug' in kwargs:
            subcategory = get_object_or_404(Subcategory,
                                            slug=kwargs['subcategory_slug'],
                                            parent=self.category,
                                            published=True)
            context['subcategory'] = subcategory
        else:
            subcategory = None

        if 'article_slug' in kwargs:
            article = get_object_or_404(NewArticle,
                                        slug=kwargs['article_slug'],
                                        published=True)
            if (self.category not in article.categories.all() and
                subcategory not in article.subcategories.all()):
                raise Http404
            context['article'] = article

        return context


class ArticleDetailView(CMSView):
    """
        Detail page for one CMS article.
    """
    template_name = 'old_cms/article_detail.html'


class CategoryDetailView(CMSView):
    """
        Detail page for a CMS category.
    """
    template_name = 'old_cms/category_detail.html'


class SubcategoryDetailView(CMSView):
    """
        Detail page for a CMS subcategory.
    """
    template_name = 'old_cms/subcategory_detail.html'


class OldPathRedirectView(RedirectView):
    """
        Redirects article URLs from the old link system.
    """
    def get_redirect_url(self, nid):
        article = get_object_or_404(NewArticle, irc_id=nid, published=True)
        return article.get_absolute_url()
