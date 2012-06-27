from django.conf.urls.defaults import include, patterns
from django.contrib import admin

from stars.apps.credits.api.urls import v1_api

admin.autodiscover()

import aashe_rules
aashe_rules.autodiscover()

urlpatterns = patterns('',
    (r'v1/credits/', include(v1_api.urls)),
    )
