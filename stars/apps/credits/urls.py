from django.conf.urls.defaults import include, patterns
from django.contrib import admin
admin.autodiscover()

import aashe_rules
aashe_rules.autodiscover()

from tastypie.api import Api
from stars.apps.credits.api.resources import *

v1_api = Api(api_name='v1')
v1_api.register(CategoryResource())
v1_api.register(CreditResource())
v1_api.register(CreditSetResource())
v1_api.register(DocumentationFieldResource())
v1_api.register(IncrementalFeatureResource())
v1_api.register(SubcategoryResource())

urlpatterns = patterns('',
    (r'v1/credits/', include(v1_api.urls)),
    )
