from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page

from stars.apps.auth.utils import respond
from stars.apps.cms.models import *
from stars.apps.helpers.shortcuts import get_cmsobject_or_404

# @cache_page(10 * 60)    # cache article details for 10 min.
def article_detail(request, category_slug, article_id):
    """Given a request for a given article in a given category, display the page"""
    category = get_object_or_404(ArticleCategory, slug=category_slug)
    article = get_cmsobject_or_404(Article, node_id=article_id, category=category)
    context = locals()
    template = "cms/article_detail.html"
    return respond(request, template, context)
    
# @cache_page(10 * 60)    # cache article lists for 10 min.
def article_list(request, category_slug): 
    """Given an article category, display a list of all articles"""
    category = get_object_or_404(ArticleCategory, slug=category_slug)
    article_list = get_cmsobject_or_404(ArticleList, category=category)
    context = locals()
    template = "cms/article_list.html"
    return respond(request, template, context)
