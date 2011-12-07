from django.conf.urls.defaults import *

from stars.apps.rules.views import OrderPizzaView

urlpatterns = patterns(
    '',

    (r'^order_pizza/(?P<topping>\w+)/(?P<charge>\d+)/$', OrderPizzaView.as_view()),
)
