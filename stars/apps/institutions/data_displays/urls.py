from django.conf.urls.defaults import *
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from stars.apps.institutions.data_displays.views import *

urlpatterns = patterns(
    'django.views.generic.simple',
    # data views
    url(r'^$',
        "direct_to_template",
        {'template': 'institutions/data_views/index.html'}),
    url(r'^pie-chart-visualization/$',
        TemplateView.as_view(
            template_name="institutions/data_displays/summary_pie_chart.html")),
    url(r'^dashboard/$', Dashboard.as_view()),

    url(r'^(?P<cs_version>[^\/]+)/categories/$',
        never_cache(AggregateFilter.as_view()),
        name="categories_data_display"),
    url(r'^(?P<cs_version>[^\/]+)/scores/$',
        never_cache(ScoreFilter.as_view()),
        name="scores_data_display"),
    url(r'^(?P<cs_version>[^\/]+)/content/$',
        never_cache(ContentFilter.as_view()),
        name="content_data_display"),

    url(r'^(?P<cs_version>[^\/]+)/scores/excel/$',
        never_cache(ScoreExcelFilter.as_view())),
    url(r'^(?P<cs_version>[^\/]+)/content/excel/$',
        never_cache(ContentExcelFilter.as_view())),
    url(r'^callback/cs/(?P<cs_id>\d+)/$',
        CategoryInCreditSetCallback.as_view()),
    url(r'^callback/cat/(?P<category_id>\d+)/$',
        SubcategoryInCategoryCallback.as_view()),
    url(r'^callback/sub/(?P<subcategory_id>\d+)/$',
        CreditInSubcategoryCallback.as_view()),
    url(r'^callback/credit/(?P<credit_id>\d+)/$',
        FieldInCreditCallback.as_view()),
)
