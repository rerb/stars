#!/usr/bin/env python
"""Restores an Institution from "stars-backup" database into
"default" db.

Also restores the Institution's SubmissionSets (and
SubcategorySubmissions, CategorySubmissions, etc.).

Specify the Institution to restore by name.

"""
from django.core.management.base import BaseCommand

from ...models import Institution
from stars.apps.credits.models import Rating
from stars.apps.institutions.models import (InstitutionPreferences,
                                            MigrationHistory,
                                            RegistrationSurvey,
                                            RespondentSurvey,
                                            StarsAccount,
                                            Subscription)
from stars.apps.submissions.models import (CreditUserSubmission,
                                           DocumentationFieldSubmission,
                                           ResponsibleParty,
                                           SubmissionSet)


class Command(BaseCommand):

    def handle(self, *args, **options):
        if len(args) == 1:
            restore_institution(name=args[0])
        else:
            print("ERROR: No Institution name specified.")
            print("USAGE: manage.py restore_institution <institution-name>")


def restore_institution(name,
                        source_db="stars-backup",
                        target_db="default"):
    """Restores Institution from `source_db` database to `target_db` db.

    You specify the Institution to restore by name.

    In addition to an Institution object, related SubmissionSets,
    Subscriptions, ResponsiblePartys, and Ratings are restored.
    SubmissionSets and Subscriptions also restore objects related to
    them.

    """
    try:
        institution_to_restore = (
            Institution.objects.using(source_db).get(name=name))
    except Institution.DoesNotExist:
        print("No Institution in {} db with name {}".format(source_db, name))
        return

    # Restore the Institution.
    print("Institution {} restoring".format(institution_to_restore.pk))
    institution_to_restore.save(using=target_db)

    # Restore SubmissionSets.
    submissionsets = Institution.objects.using(
        source_db).get(
            pk=institution_to_restore.pk).submissionset_set.all().order_by("-pk")  # noqa

    for submissionset in submissionsets:
        restore_submissionset(submissionset=submissionset,
                              source_db=source_db,
                              target_db=target_db)

    # Restore Subscriptions.
    subscriptions = Subscription.objects.using(source_db).filter(
        institution=institution_to_restore)

    for subscription in subscriptions:
        restore_subscription(subscription=subscription,
                             source_db=source_db,
                             target_db=target_db)

    # Restore ResponsiblePartys.
    for responsible_party in ResponsibleParty.objects.using(
            source_db).filter(institution=institution_to_restore):
        print("\t\tResponsible Party {} restoring".format(
            responsible_party.pk))
        responsible_party.save(using=target_db)
        print("\t\tResponsible Party {} restored".format(
            responsible_party.pk))

    # Restore StarsAccounts.
    for stars_account in StarsAccount.objects.using(
            source_db).filter(institution=institution_to_restore):
        print("\t\tSTARS Account {} restoring".format(stars_account.pk))
        stars_account.save(using=target_db)
        print("\t\t\tUser {} restoring".format(stars_account.user.pk))
        stars_account.user.save(using=target_db)
        print("\t\t\tUser {} restored".format(stars_account.user.pk))
        print("\t\tSTARS Account {} restored".format(stars_account.pk))

    # Restore MigrationHistorys.
    for migration_history in MigrationHistory.objects.using(
            source_db).filter(institution=institution_to_restore):
        print("\t\tMigrationHistory {} restoring".format(migration_history.pk))
        migration_history.save(using=target_db)
        print("\t\tMigrationHistory {} restored".format(migration_history.pk))

    # Restore RegistrationSurveys.
    for registration_survey in RegistrationSurvey.objects.using(
            source_db).filter(institution=institution_to_restore):
        print("\t\tRegistrationSurvey {} restoring".format(
            registration_survey.pk))
        registration_survey.save(using=target_db)
        print("\t\tRegistrationSurvey {} restored".format(
            registration_survey.pk))

    # Restore RespondentSurveys.
    for respondent_survey in RespondentSurvey.objects.using(
            source_db).filter(institution=institution_to_restore):
        print("\t\tRespondentSurvey {} restoring".format(respondent_survey.pk))
        respondent_survey.save(using=target_db)
        print("\t\tRespondentSurvey {} restored".format(respondent_survey.pk))

    # Restore InstitutionPreferences.
    for institution_preference in InstitutionPreferences.objects.using(
            source_db).filter(institution=institution_to_restore):
        print("\t\tInstitutionPreference {} restoring".format(
            institution_preference.pk))
        institution_preference.save(using=target_db)
        print("\t\tInstitutionPreference {} restored".format(
            institution_preference.pk))

    print("Institution {} restored".format(institution_to_restore.pk))


def restore_submissionset(submissionset,
                          source_db="stars-backup",
                          target_db="default"):
    """Restores `submissionset` and related CategorySubmissions from
    `source_db` to `target_db`.

    """
    print("\tSubmissionSet {} restoring".format(submissionset.pk))
    date_created = submissionset.date_created
    submissionset.save(using=target_db,
                       skip_init_credit_submissions=True,
                       invalidate_cache=False)
    submissionset.date_created = date_created
    submissionset.save(using=target_db,
                       skip_init_credit_submissions=True,
                       invalidate_cache=False)

    category_submissions_to_restore = (
        submissionset.categorysubmission_set.using(source_db).all())
    for category_submission in category_submissions_to_restore:
        restore_category_submission(category_submission,
                                    source_db,
                                    target_db)

    if submissionset.rating_id:
        print("\t\tRating {} restoring".format(submissionset.rating_id))
        rating = Rating.objects.using(source_db).get(
            submissionset=submissionset)
        rating.save(using=target_db)
        print("\t\tRating {} restored".format(rating.pk))

    print("\tSubmissionSet {} restored".format(submissionset.pk))


def restore_category_submission(category_submission, source_db, target_db):
    """Restores `category_submission` and all related SubcategorySubmissions.
    """

    print("\t\tCategorySubmission {} restoring".format(
        category_submission.pk))
    category_submission.save(using=target_db)

    subcategory_submissions_to_restore = (
        category_submission.subcategorysubmission_set.using(source_db).all())
    for sub_category_submission in subcategory_submissions_to_restore:
        restore_subcategory_submission(sub_category_submission,
                                       source_db,
                                       target_db)

    print("\t\tCategorySubmission {} restored".format(
        category_submission.pk))


def restore_subcategory_submission(subcategory_submission,
                                   source_db,
                                   target_db):
    """Restores `subcategory_submission` and all related
    CreditSubmissions.

    """

    print("\t\t\tSubCategorySubmission {} restoring".format(
        subcategory_submission.pk))
    subcategory_submission.save(using=target_db)

    credit_user_submissions_to_restore = (
        subcategory_submission.creditusersubmission_set.using(
            source_db).all())
    for credit_user_submission in credit_user_submissions_to_restore:
        restore_credit_user_submission(credit_user_submission,
                                       source_db,
                                       target_db)

    print("\t\t\tSubCategorySubmission {} restored".format(
        subcategory_submission.pk))


def restore_credit_user_submission(credit_user_submission,
                                   source_db,
                                   target_db):
    """Restores `credit_user_submission` and all related
    DocumentationFieldSubmissions.

    """

    print("\t\t\t\tCreditUserSubmission {} restoring".format(
        credit_user_submission.pk))
    credit_user_submission.save(using=target_db,
                                calculate_points=False)

    credit_user_submission = CreditUserSubmission.objects.using(
        source_db).get(pk=credit_user_submission.pk)

    documentation_field_submissions_to_restore = (
        get_documentation_field_submissions(
            credit_user_submission=credit_user_submission,
            source_db=source_db))

    for documentation_field_submission in (
            documentation_field_submissions_to_restore):

        restore_documentation_field_submission(
            documentation_field_submission=documentation_field_submission,
            source_db=source_db,
            target_db=target_db)

    print("\t\t\t\tCreditUserSubmission {} restored".format(
        credit_user_submission.pk))


def get_documentation_field_submissions(credit_user_submission,
                                        source_db):
    """Returns DocumentationFieldSubmissions for `credit_user_submission`.
    """
    documentation_field_submissions = []

    for documentation_field in (
            credit_user_submission.credit.documentationfield_set.using(
                source_db).all()):
        SubmissionFieldModelClass = (
            DocumentationFieldSubmission.get_field_class(
                documentation_field))
        if SubmissionFieldModelClass:
            try:
                submission_field = SubmissionFieldModelClass.objects.using(
                    source_db).get(documentation_field=documentation_field,
                                   credit_submission=credit_user_submission)
            except SubmissionFieldModelClass.DoesNotExist:
                pass
            else:
                documentation_field_submissions.append(submission_field)
        else:
            # TabularSubmissionField, just skip it.
            pass

    return documentation_field_submissions


def restore_documentation_field_submission(
        documentation_field_submission,
        source_db,
        target_db):

    print("\t\t\t\t\tDocumentationFieldSubmission {} restoring".format(
        documentation_field_submission.pk))

    documentation_field_submission.save(using=target_db)

    print("\t\t\t\t\tDocumentationFieldSubmission {} restored".format(
        documentation_field_submission.pk))


def restore_subscription(subscription,
                         source_db,
                         target_db):
    """Restores `subscription` and all related SubscriptionPayments.

    """

    print("\t\t\t\tSubscription {} restoring".format(subscription.pk))
    subscription.save(using=target_db)

    for subscription_payment in subscription.subscriptionpayment_set.all():
        print("\t\t\t\t\tSubscriptionPayment {} restoring".format(
            subscription_payment.pk))
        subscription_payment.save(using=target_db, subscription=subscription)
        print("\t\t\t\t\tSubscriptionPayment {} restored".format(
            subscription_payment.pk))

    print("\t\t\t\tSubscription {} restored".format(
        subscription.pk))


def restore_only_document_field_submissions(institution,
                                            source_db="stars-backup",
                                            target_db="default"):
    submissionsets = Institution.objects.using(
        source_db).get(
            pk=institution.pk).submissionset_set.all()

    for submissionset in submissionsets:

        if not SubmissionSet.objects.using(target_db).filter(
                    pk=submissionset.pk).count():
            continue

        category_submissions_to_restore = (
            submissionset.categorysubmission_set.using(source_db).all())
        for category_submission in category_submissions_to_restore:

            subcategory_submissions_to_restore = (
                category_submission.subcategorysubmission_set.using(source_db).all())  # noqa
            for subcategory_submission in subcategory_submissions_to_restore:

                credit_user_submissions_to_restore = (
                    subcategory_submission.creditusersubmission_set.using(
                        source_db).all())
                for credit_user_submission in (
                        credit_user_submissions_to_restore):

                    # First, clear any documentation_field_submissions for this
                    # credit_user_submission from the target db.
                    documentation_field_submissions_to_clear = (
                        get_documentation_field_submissions(
                            credit_user_submission=credit_user_submission,
                            source_db=target_db))
                    for documentation_field_submission in (
                            documentation_field_submissions_to_clear):
                        documentation_field_submission.delete()

                    documentation_field_submissions_to_restore = (
                        get_documentation_field_submissions(
                            credit_user_submission=credit_user_submission,
                            source_db=source_db))

                    for documentation_field_submission in (
                            documentation_field_submissions_to_restore):

                        restore_documentation_field_submission(
                            documentation_field_submission=documentation_field_submission,
                            source_db=source_db,
                            target_db=target_db)
