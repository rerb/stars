"""
    subscription_etl.py

    prereqs:
        - ISS is synced with the latest membersuite ids

    This management command connects to MemberSuite using the
    `python_membersuite_api_client` library.

    This sync simply matches on the `membersuite_id` column,

    default match fields:
        ['membersuite_id']
"""

from django.core.management.base import BaseCommand
from django.conf import settings

from membersuite_api_client.client import ConciergeClient
from membersuite_api_client.subscriptions.services import SubscriptionService
from stars.apps.institutions.models import MemberSuiteInstitution, Subscription


class Command(BaseCommand):
    """
        USAGE: manage.py subscription_etl

        Syncs subscriptions from Membersuite
    """

    def handle(self, *args, **options):
        self.get_subscriptions()

    def get_subscriptions(self, verbose=False):
        client = ConciergeClient(
            access_key=settings.MS_ACCESS_KEY,
            secret_key=settings.MS_SECRET_KEY,
            association_id=settings.MS_ASSOCIATION_ID)
        service = SubscriptionService(client=client)

        # store a list of existing subscription id's
        # those that aren't found in the update, will be removed
        local_subscription_ids = Subscription.objects.values_list(
            'id', flat=True)

        # pull subscriptions from Membersuite
        ms_subscription_list = service.get_subscriptions(
                limit_to=3,
                max_calls=3,
                publication_id=settings.STARS_MS_PUBLICATION_ID,
                verbose=verbose)

        # loop through each MS Subscription
        # add/update local subscriptions as necessary
        # remove from local_subscription_ids so it won't be removed
        for ms_sub in ms_subscription_list:

            # is it an existing subscription?
            if ms_sub.id in local_subscription_ids:
                local_sub = Subscription.objects.get(ms_id=ms_sub.id)
                # remove this from the list of subscriptions to be removed
                local_subscription_ids.remove(local_sub.id)
            else:
                # add a new subscription
                local_sub = Subscription()

            # update and save the local subscription
            self.update_subscription_from_iss(local_sub, ms_sub)
            local_sub.save()

        # if any id's remain in subscription_id_list they can be removed
        # from the local list as they don't exist in MemberSuite anymore
        for sub_id in local_subscription_ids:
            Subscription.objects.get(id=sub_id).delete()

    def update_subscription_from_iss(self, local_sub, iss_sub):
        """ Copy the fields over from stars """

        if not local_sub.ms_id:
            local_sub.ms_id = iss_sub.id

        local_sub.ms_institution = MemberSuiteInstitution.objects.get(
            membersuite_account_num=iss_sub.org_id)

        local_sub.start_date = iss_sub.start
        local_sub.end_date = iss_sub.end

        return local_sub
