from django.conf.urls import include, patterns
from django.contrib import admin

from stars.apps.credits.api.urls import api

import logical_rules
logical_rules.autodiscover()

urlpatterns = patterns('',
                       (r'0.1/credits/', include(api.urls)),
                       )
