from django.conf.urls import patterns, url
from django.views.decorators.cache import never_cache

from views import InstitutionList

urlpatterns = patterns(
    'stars.apps.tool.staff_tool.views',

    # Institutional Admin
    (r'^$', InstitutionList.as_view()),
    (r'^search/$', 'institutions_search'),
    (r'^list$', InstitutionList.as_view()),
    (r'^institution/masquerade/(?P<id>\d+)/$', 'select_institution'),

)
