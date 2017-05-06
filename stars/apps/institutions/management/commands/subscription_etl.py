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
from __future__ import unicode_literals

import datetime
import logging
import pickle

from django.core.management.base import BaseCommand
from django.conf import settings

from membersuite_api_client.organizations.services import OrganizationService
from membersuite_api_client.security.services import (
    get_user_for_membersuite_entity)
from membersuite_api_client.subscriptions.services import SubscriptionService
from membersuite_api_client.utils import get_new_client

from stars.apps.institutions.management.commands.preloaded_subscription_names \
    import PRELOADED_SUBSCRIPTION_NAMES
from stars.apps.institutions.models import (Institution,
                                            MemberSuiteInstitution,
                                            Subscription)
from stars.apps.institutions.utils import update_institution_properties
from stars.apps.registration.utils import (init_starsaccount,
                                           init_submissionset)


MEMBERSUITE_PREPRODUCTION_DATA_LOAD = datetime.datetime(2017, 4, 9, 20, 0)

pickler = None

logger = logging.getLogger()


class NoSTARSLiaisonError(Exception):
    pass


def get_access_level(membersuite_subscription, client):
    """Return the access level for `membersuite_subscription`.

    Note a big assumption made here: namely, that the first line
    item on the Order for this Subscription is for this
    Subscription.  I.e., this Subscription doesn't appear in any
    order line except the first.

    """
    order = membersuite_subscription.get_order(client=client)

    if order:
        products = order.get_products(client=client)
        for product in products:
            if "full" in product.name.lower():
                return Subscription.FULL_ACCESS
            elif "basic" in product.name.lower():
                return Subscription.BASIC_ACCESS

    elif ((membersuite_subscription.fields["CreatedDate"] ==
           MEMBERSUITE_PREPRODUCTION_DATA_LOAD) and
          membersuite_subscription.name in PRELOADED_SUBSCRIPTION_NAMES):
        return Subscription.FULL_ACCESS

    return Subscription.BASIC_ACCESS  # default


class Command(BaseCommand):
    """
        USAGE: manage.py subscription_etl

        Syncs subscriptions from Membersuite
    """

    client = get_new_client(request_session=True)

    def handle(self, verbose=True, *args, **options):
        self.sync_subscriptions(verbose=verbose)

    def get_subscriptions(self, verbose=True):
        service = SubscriptionService(client=self.client)

        # pull subscriptions from Membersuite
        membersuite_subscription_list = service.get_subscriptions(
            publication_id=settings.STARS_MS_PUBLICATION_ID,
            verbose=verbose)

        return membersuite_subscription_list

    def update_subscription_from_membersuite(self, stars_subscription,
                                             membersuite_subscription):

        stars_subscription.ms_id = membersuite_subscription.membersuite_id
        stars_subscription.start_date = membersuite_subscription.start_date
        stars_subscription.end_date = membersuite_subscription.expiration_date
        stars_subscription.name = membersuite_subscription.name

        stars_subscription.access_level = get_access_level(
            membersuite_subscription=membersuite_subscription,
            client=self.client)

        try:
            ms_institution = (MemberSuiteInstitution.objects.get(
                membersuite_account_num=membersuite_subscription.owner_id))
        except MemberSuiteInstitution.DoesNotExist:
            print("ERROR: No MemberSuiteInstitution for "
                  "membersuite_subscription: "
                  "(sub) {}, (name) {}, (owner id) {}".format(
                      membersuite_subscription.membersuite_id,
                      membersuite_subscription.name,
                      membersuite_subscription.owner_id))
            # OR should we create a MemberSuiteInstitution?
        else:
            stars_subscription.ms_institution = ms_institution

            try:
                stars_subscription.institution = Institution.objects.get(
                    ms_institution=stars_subscription.ms_institution)
            except Institution.DoesNotExist:
                # Make one.
                institution = Institution(name=ms_institution.org_name,
                                          ms_institution=ms_institution)
                institution.update_from_iss()
                institution.set_slug_from_iss_institution(institution.aashe_id)

                services = OrganizationService(client=self.client)

                membersuite_stars_liaison = (
                    services.get_stars_liaison_for_organization(
                        organization=ms_institution))

                if not membersuite_stars_liaison:
                    logger.error(
                        "No STARS Liaison for Institution '{}'".format(
                            institution.name))
                    raise NoSTARSLiaisonError

                self.update_institution_contact_info(
                    institution=institution,
                    liaison=membersuite_stars_liaison)

                # institution must have a pk before creating related
                # StarsAccount and SubmissionSet records, so save it
                # now:
                institution.save()

                user, _ = get_user_for_membersuite_entity(
                    membersuite_entity=membersuite_stars_liaison)

                # Make a STARS Account:
                init_starsaccount(user, institution)

                # Make Submission Set:
                init_submissionset(institution, user)

            if stars_subscription.institution:
                update_institution_properties(stars_subscription.institution)

    def update_institution_contact_info(self, institution, liaison):
        institution.contact_first_name = liaison.first_name
        institution.contact_last_name = liaison.last_name
        institution.contact_title = liaison.title
        institution.contact_phone = liaison.phone_number
        institution.contact_email = liaison.email_address

    def sync_subscriptions(self, verbose=True):

        global pickler

        # store a list of existing subscription id's
        # those that aren't found in the update, will be removed
        stars_subscription_ms_ids = list(
            Subscription.objects.values_list("ms_id", flat=True))

        membersuite_subscription_list = self.get_subscriptions(verbose=verbose)

        with open("pickle.jar", "wb") as f:
            pickler = pickle.Pickler(f)

            # loop through each MS Subscription
            # add/update local subscriptions as necessary
            # remove from stars_subscription_ids so it won't be archived
            for membersuite_subscription in membersuite_subscription_list:

                # is it an existing subscription?
                if (membersuite_subscription.membersuite_id in
                    stars_subscription_ms_ids):  # noqa

                    stars_subscription = Subscription.objects.get(
                        ms_id=membersuite_subscription.membersuite_id)
                    # remove this from the list of subscriptions to be archived
                    del(stars_subscription_ms_ids[
                        stars_subscription_ms_ids.index(
                            stars_subscription.ms_id)])
                else:
                    # add a new subscription
                    stars_subscription = Subscription(
                        ms_id=membersuite_subscription.membersuite_id)

                # update and save the local subscription
                try:
                    self.update_subscription_from_membersuite(
                        stars_subscription,
                        membersuite_subscription)
                except NoSTARSLiaisonError:
                    next

                stars_subscription.save()

                if stars_subscription.institution:
                    stars_subscription.institution.update_status()
                    stars_subscription.institution.save()

            # if any id's remain in subscription_id_list they can be archived
            # as they don't exist in MemberSuite anymore
            for ms_id in stars_subscription_ms_ids:
                Subscription.objects.filter(ms_id=ms_id).update(archived=True)
