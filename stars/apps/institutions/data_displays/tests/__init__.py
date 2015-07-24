from stars.apps.institutions.data_displays.tests.models import (
    AuthorizedUserTestCase)
from stars.apps.institutions.data_displays.tests.filters import (
    FilterTestCase)
from stars.apps.institutions.data_displays.tests.views import (
    AggregateFilterTestCase,
    ContentFilterTestCase,
    DashboardTestCase,
    ScoreFilterTestCase)

__test__ = {
    'AggregateFilterTestCase,': AggregateFilterTestCase,
    'AuthorizedUserTestCase': AuthorizedUserTestCase,
    'ContentFilterTestCase': ContentFilterTestCase,
    'DashboardTestCase': DashboardTestCase,
    'FilterTestCase': FilterTestCase,
    'ScoreFilterTestCase': ScoreFilterTestCase
}
