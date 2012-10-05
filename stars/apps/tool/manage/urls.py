from django.conf.urls.defaults import patterns, url
from views import (AccountCreateView, AccountDeleteView, AccountEditView,
                   AccountListView, ContactView, InstitutionPaymentsView,
                   MigrateDataView, MigrateOptionsView,
                   PendingAccountDeleteView,
                   ResponsiblePartyCreateView, ResponsiblePartyDeleteView,
                   ResponsiblePartyEditView, ResponsiblePartyListView,
                   ShareDataView)

urlpatterns = patterns(
    'stars.apps.tool.manage.views',

    url(r'^contact/$', ContactView.as_view(), name='institution-contact'),

    url(r'^payments/$', InstitutionPaymentsView.as_view(),
        name='institution-payments'),

    # Responsible Party views:
    url(r'^responsible-party/$',
        ResponsiblePartyListView.as_view(),
        name='responsible-party-list'),

    url(r'^responsible-party/create/$',
        ResponsiblePartyCreateView.as_view(),
        name='responsible-party-create'),

    url(r'^responsible-party/(?P<pk>\d+)/$',
        ResponsiblePartyEditView.as_view(),
        name='responsible-party-edit'),

    url(r'^responsible-party/(?P<pk>\d+)/delete/$',
        ResponsiblePartyDeleteView.as_view(),
        name='responsible-party-delete'),

    # User/Account views:
    url(r'^user/$', AccountListView.as_view(),
        name='account-list'),

    url(r'^user/create/$', AccountCreateView.as_view(),
        name='account-create'),

    url(r'^user/edit/(?P<pk>\d+)/$', AccountEditView.as_view(),
        name='account-edit'),

    url(r'^user/delete/(?P<pk>\d+)/$', AccountDeleteView.as_view(),
        name='account-delete'),

    url(r'^pending-user/delete/(?P<pk>\d+)/$',
        PendingAccountDeleteView.as_view(),
        name='pending-account-delete'),

    url(r'^share-data/$', ShareDataView.as_view(),
        name='share-data'),

    url(r'^migrate/$', MigrateOptionsView.as_view(),
        name='migrate-options'),

    url(r'^migrate/data/(?P<pk>\d+)/$', MigrateDataView.as_view(),
        name='migrate-data'),

    url(r'^migrate/version/$', 'migrate_version',
        name='migrate-version'),

    url(r'^purchase-subscription/', 'purchase_subscription',
        name='purchase-subscription'),

    url(r'^pay-subscription/(?P<subscription_id>\d+)/$', 'pay_subscription',
        name='pay-subscription'),
)
