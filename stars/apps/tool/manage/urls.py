from django.conf.urls.defaults import patterns, url
from views import AccountCreateView, ContactView, InstitutionPaymentsView, \
     ResponsiblePartyCreateView, ResponsiblePartyDeleteView, \
     ResponsiblePartyEditView, ResponsiblePartyListView

urlpatterns = patterns(
    'stars.apps.tool.manage.views',

    url(r'^contact/$', ContactView.as_view(), name='institution-contact'),

    url(r'^payments/$', InstitutionPaymentsView.as_view(),
        name='institution-payments'),

    url(r'^responsible-parties/$', ResponsiblePartyListView.as_view(),
        name='responsible-party-list'),

    url(r'^responsible-party/create/$', ResponsiblePartyCreateView.as_view(),
        name='responsible-party-create'),

    url(r'^responsible-party/(?P<pk>\d+)/$',
        ResponsiblePartyEditView.as_view(), name='responsible-party-edit'),

    url(r'^responsible-party/(?P<pk>\d+)/delete/$',
        ResponsiblePartyDeleteView.as_view(),
        name='responsible-party-delete'),

    url(r'^users/$', 'accounts', name='account-list'),

    url(r'^users/create/$', AccountCreateView.as_view(),
        name='account-create'),

    (r'^users/old-add/$', 'add_account'),

    # (r'^users/edit/(?P<account_id>\d+)/$', 'account-edit'),
    # (r'^users/delete/(?P<account_id>\d+)/$', 'account-delete'),
    url(r'^users/edit/(?P<pk>\d+)/$', 'accounts', name='account-edit'),
    url(r'^users/delete/(?P<pk>\d+)/$', 'delete_account',
        name='account-delete'),

    (r'^share-data/$', 'share_data'),

    (r'^migrate/$', 'migrate_options'),
    (r'^migrate/data/(?P<ss_id>\d+)/$', 'migrate_data'),
    (r'^migrate/version/$', 'migrate_version'),

    (r'^purchase-subscription/', 'purchase_subscription'),
    (r'^pay-subscription/(?P<subscription_id>\d+)/$', 'pay_subscription'),
)
