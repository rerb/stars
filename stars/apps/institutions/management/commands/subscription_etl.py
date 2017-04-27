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
import pickle

from django.core.management.base import BaseCommand
from django.conf import settings

from membersuite_api_client.client import ConciergeClient
from membersuite_api_client.subscriptions.services import SubscriptionService
from stars.apps.institutions.models import (Institution,
                                            MemberSuiteInstitution,
                                            Subscription)
from stars.apps.institutions.utils import update_one_institutions_properties


pickler = None


class Command(BaseCommand):
    """
        USAGE: manage.py subscription_etl

        Syncs subscriptions from Membersuite
    """

    def handle(self, verbose=True, *args, **options):
        self.sync_subscriptions(verbose=verbose)

    def get_subscriptions(self, verbose=True):
        client = ConciergeClient(
            access_key=settings.MS_ACCESS_KEY,
            secret_key=settings.MS_SECRET_KEY,
            association_id=settings.MS_ASSOCIATION_ID)
        service = SubscriptionService(client=client)

        # pull subscriptions from Membersuite
        ms_subscription_list = service.get_subscriptions(
                publication_id=settings.STARS_MS_PUBLICATION_ID,
                verbose=verbose)

        return ms_subscription_list

    def sync_subscriptions(self, verbose=True):

        global pickler

        # store a list of existing subscription id's
        # those that aren't found in the update, will be removed
        local_subscription_ids = Subscription.objects.values_list('id',
                                                                  flat=True)

        ms_subscription_list = self.get_subscriptions(verbose=verbose)

        with open("pickle.jar", "wb") as f:
            pickler = pickle.Pickler(f)

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
                self.update_subscription_from_membersuite(local_sub, ms_sub)
                local_sub.save()

            # if any id's remain in subscription_id_list they can be removed
            # from the local list as they don't exist in MemberSuite anymore
            for sub_id in local_subscription_ids:
                Subscription.objects.filter(id=sub_id).update(archived=True)

    def update_subscription_from_membersuite(self, local_sub, ms_sub):

        if not local_sub.ms_id:
            local_sub.ms_id = ms_sub.id

        try:
            local_sub.ms_institution = MemberSuiteInstitution.objects.get(
                membersuite_account_num=ms_sub.org_id)
        except MemberSuiteInstitution.DoesNotExist:
            print "ERROR: No MemberSuiteInstitution for ms_sub: {}: {}".format(
                ms_sub.id, ms_sub.org_id)
            # OR should we create a MemberSuiteInstitution?
        else:
            assert(local_sub.ms_institution is not None)
            try:
                local_sub.institution = Institution.objects.get(
                    ms_institution=local_sub.ms_institution)
            except Institution.DoesNotExist:
                print "ERROR: No Institution for MS Subscription: {}: {}".format(
                    ms_sub.id, local_sub.ms_institution.org_name.encode("utf-8"))
                pickler.dump(local_sub)
            else:
                update_one_institutions_properties(local_sub.institution)

        local_sub.start_date = ms_sub.start
        local_sub.end_date = ms_sub.end
