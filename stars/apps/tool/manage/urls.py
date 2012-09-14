from django.conf.urls.defaults import patterns, url
from views import ContactView, InstitutionPaymentsView, \
     ResponsiblePartyEditView, ResponsiblePartyListView

urlpatterns = patterns(
    'stars.apps.tool.manage.views',

    url(r'^contact/$', ContactView.as_view(), name='institution-contact'),
    url(r'^payments/$', InstitutionPaymentsView.as_view(),
        name='institution-payments'),
    url(r'^responsible-parties/$', ResponsiblePartyListView.as_view(),
        name='responsible-party-list'),
    (r'^responsible-parties/add/$', 'add_responsible_party'),
    url(r'^responsible-party/(?P<pk>\d+)/$',
        ResponsiblePartyEditView.as_view(), name='responsible-party-edit'),
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
