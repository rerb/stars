from django.conf.urls.defaults import patterns, url
from views import AccountCreateView, ContactView, InstitutionPaymentsView, \
     ResponsiblePartyCreateView, ResponsiblePartyDeleteView, \
     ResponsiblePartyEditView, ResponsiblePartyListView

urlpatterns = patterns(
    'stars.apps.tool.manage.views',

    url(r'^contact/$', ContactView.as_view(), name='institution-contact'),

    url(r'^payments/$', InstitutionPaymentsView.as_view(),
        name='institution-payments'),

    # Responsible Party views:
    url(r'^responsible-party/$', ResponsiblePartyListView.as_view(),
        name='responsible-party-list'),

    url(r'^responsible-party/create/$', ResponsiblePartyCreateView.as_view(),
        name='responsible-party-create'),

    url(r'^responsible-party/(?P<pk>\d+)/$',
        ResponsiblePartyEditView.as_view(), name='responsible-party-edit'),

    url(r'^responsible-party/(?P<pk>\d+)/delete/$',
        ResponsiblePartyDeleteView.as_view(),
        name='responsible-party-delete'),

    # User/Account views:
    url(r'^user/$', 'accounts',
        name='account-list'),

    url(r'^user/create/$', AccountCreateView.as_view(),
        name='account-create'),

    url(r'^user/edit/(?P<pk>\d+)/$', 'accounts',
        name='account-edit'),
    url(r'^user/delete/(?P<pk>\d+)/$', 'delete_account',
        name='account-delete'),

    (r'^share-data/$', 'share_data'),

    (r'^migrate/$', 'migrate_options'),
    (r'^migrate/data/(?P<ss_id>\d+)/$', 'migrate_data'),
    (r'^migrate/version/$', 'migrate_version'),

    (r'^purchase-subscription/', 'purchase_subscription'),
    (r'^pay-subscription/(?P<subscription_id>\d+)/$', 'pay_subscription'),
)
