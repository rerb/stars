from django.conf.urls.defaults import patterns, url
from views import ContactView, InstitutionPaymentsView

urlpatterns = patterns(
    'stars.apps.tool.manage.views',

    (r'^contacts/$', ContactView.as_view()),
    url(r'^payments/$', InstitutionPaymentsView.as_view(),
        name='institution-payments'),
    (r'^responsible-parties/$', 'responsible_party_list'),
    (r'^responsible-parties/add/$', 'add_responsible_party'),
    (r'^responsible-parties/(?P<rp_id>\d+)/$', 'edit_responsible_party'),
    (r'^responsible-parties/(?P<rp_id>\d+)/delete/$', 'delete_responsible_party'),
    (r'^users/$', 'accounts'),
    (r'^users/add/$', 'add_account'),
    (r'^users/edit/(?P<account_id>\d+)/$', 'accounts'),
    (r'^users/delete/(?P<account_id>\d+)/$', 'delete_account'),
    (r'^share-data/$', 'share_data'),

    (r'^migrate/$', 'migrate_options'),
    (r'^migrate/data/(?P<ss_id>\d+)/$', 'migrate_data'),
    (r'^migrate/version/$', 'migrate_version'),

    (r'^purchase-subscription/', 'purchase_subscription'),
    (r'^pay-subscription/(?P<subscription_id>\d+)/$', 'pay_subscription'),
)
