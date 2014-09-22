import copy
import datetime

from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import (Boundary,
                                           CreditTestSubmission,
                                           CreditUserSubmission,
                                           DocumentationFieldSubmission,
                                           PENDING_SUBMISSION_STATUS,
                                           SubcategorySubmission,
                                           SubmissionSet)


def migrate_creditset(old_cs, new_version_name, release_date):
    """
        Copy a creditset to a new version and update `previous_version`
        references
    """

    def migrate_obj(old_obj, prop_dict, previous=True):

        new_obj = copy.copy(old_obj)
        new_obj.id = None
        if previous:
            new_obj.previous_version = old_obj
        for k,v in prop_dict.items():
            setattr(new_obj, k, v)
        new_obj.save()
        return new_obj

    new_cs = migrate_obj(old_cs, {'version': new_version_name,
                                  'release_date': release_date})

    # ratings
    for r in old_cs.rating_set.all():
        new_r = migrate_obj(r, {'creditset': new_cs,})

    # categories, subcategories, credits, applicability reasons,
    # documentation field, choice
    for cat in old_cs.category_set.all():
        new_cat = migrate_obj(cat, {'creditset': new_cs,})

        for sub in cat.subcategory_set.all():
            new_sub = migrate_obj(sub, {'category': new_cat,})

            for credit in sub.credit_set.all():
                new_c = migrate_obj(credit, {'subcategory': new_sub,})

                for ar in credit.applicabilityreason_set.all():
                    new_ar = migrate_obj(ar, {'credit': new_c,})

                for field in credit.documentationfield_set.order_by('-id'):
                    new_f = migrate_obj(field, {'credit': new_c,})

                    for choice in field.choice_set.all():
                        new_choice = migrate_obj(
                            choice,
                            {'documentation_field': new_f})

                for cts in CreditTestSubmission.objects.filter(credit=credit):
                    new_cts = CreditTestSubmission(
                        credit=new_c,
                        expected_value=cts.expected_value)
                    new_cts.save()

                    for dfs in cts.get_submission_fields():
                        new_field = dfs.documentation_field.next_version
                        new_dfs = DocumentationFieldSubmission.get_field_class(
                            dfs.documentation_field)(
                                value=dfs.value,
                                documentation_field=dfs.documentation_field.next_version,
                                credit_submission=new_cts)
                        new_dfs.save()
    return new_cs


def create_ss_mirror(old_ss, new_cs=None,
                     registering_user=None,
                     keep_innovation=False,
                     keep_status=False):
    """

        and migrates the data from old_ss leaving it unchanged

        takes an optional creditset to use
    """
    new_ss = _new_submissionset_for_old_submissionset(old_ss,
                                                      new_cs,
                                                      registering_user)
    return migrate_submission(old_ss, new_ss,
                              keep_innovation=keep_innovation,
                              keep_status=keep_status)


def _new_submissionset_for_old_submissionset(old_ss,
                                             new_cs=None,
                                             registering_user=None):
    """
        Returns a new SubmissionSet based on existing submissionset
        `old_ss`, using CreditSet `new_cs` or, if not specified, the
        latest CreditSet.

        If `registering_user` is provided, it's tacked on to the
        new SubmissionSet, otherwise, the registering_user from
        `old_ss` is copied.
    """
    new_cs = new_cs or CreditSet.objects.get_latest()

    new_ss = SubmissionSet(creditset=new_cs,
                           institution=old_ss.institution,
                           date_registered=old_ss.date_registered,
                           status=PENDING_SUBMISSION_STATUS,
                           is_locked=True,
                           is_visible=False,
                           date_created=datetime.date.today())

    new_ss.registering_user = registering_user or old_ss.registering_user

    new_ss.save()

    return new_ss

def migrate_ss_version(old_ss, new_cs):
    """
        Migrate a SubmissionSet from one CreditSet version to another

        - Locks the old submission.
        - Creates the new hidden one
        - Migrates the data
        - Hides the old one
        - Unhides the new one and makes it active
        - Returns the new submissionset
    """
    if not old_ss.is_locked:
        old_ss.is_locked = True
        old_ss.save()

    new_ss = create_ss_mirror(old_ss, new_cs)

    new_ss.is_locked = False
    new_ss.is_visible = True
    new_ss.migrated_from = old_ss
    new_ss.save()

    # make active submission set
    new_ss.institution.set_active_submission(new_ss)

    old_ss.is_visible = False
    old_ss.save()

    return new_ss


def migrate_submission(old_ss, new_ss, keep_status=False, keep_innovation=False):
    """
        Migrate data from one SubmissionSet to another

        Keeping the status will keep the submission status the same
        and transfer all the properties UNLESS the submissionsets
        are of different versions.

        Note: don't migrate IN data if the previous submission was rated,
        unless indicated (in the case of a snapshot)
    """
    # if the old SubmissionSet hasn't been initialized we don't have
    # to do much:
    if old_ss.categorysubmission_set.count() == 0:
        new_ss.migrated_from = old_ss
        new_ss.save()
        return new_ss

    # check if we can migrate innovation data
    migrate_innovation_category = True

    if old_ss.status == "r" and not keep_innovation:
        migrate_innovation_category = False

    # Since there is currently no change necessary with the category
    # we will ignore it.

    # I'm keeping this in here in case we add data to the
    # CategorySubmission objects

    # for cat in new_ss.categorysubmission_set.all():
    #     try:
    #         old_cat = ss.categorysubmission_set.get(
    #             category=cat.category.previous_version)
    #     except CategorySubmission.DoesNotExist:
    #         continue

    # Get all SubcategorySubmissions in this SubmissionSet regardless
    # of Category
    ss_set = SubcategorySubmission.objects.filter(
        category_submission__submissionset=new_ss)
    if not migrate_innovation_category:
        ss_set = ss_set.exclude(
            category_submission__category__abbreviation="IN")

    for sub in ss_set:
        # get the related subcategory
        prev_sub = sub.subcategory.get_for_creditset(old_ss.creditset)

        # if it has a previous version
        if prev_sub:
            try:
                old_sub = SubcategorySubmission.objects.get(
                    category_submission__submissionset=old_ss,
                    subcategory=prev_sub)
                sub.description = old_sub.description
                sub.save()
            except SubcategorySubmission.DoesNotExist:
                # This must be a new subcategory
                continue
        else:
            pass

    c_set = CreditUserSubmission.objects.filter(
        subcategory_submission__category_submission__submissionset=new_ss)
    if not migrate_innovation_category:
        c_set = c_set.exclude(subcategory_submission__category_submission__category__abbreviation="IN")

    for c in c_set:

        # find the parent credit
        prev_credit = c.credit.get_for_creditset(old_ss.creditset)

        if prev_credit:
            try:
                old_c = CreditUserSubmission.objects.get(
                    subcategory_submission__category_submission__submissionset=old_ss,
                    credit=prev_credit)

                c.last_updated = old_c.last_updated
                try:
                    c.user = old_c.user
                except:
                    c.user = None
                c.internal_notes = old_c.internal_notes
                c.submission_notes = old_c.submission_notes
                c.responsible_party = old_c.responsible_party

                # can only keep status if the
                if (keep_status and
                    old_ss.creditset.version == new_ss.creditset.version):
                    c.submission_status = old_c.submission_status
                    c.responsible_party_confirm = (
                        old_c.responsible_party_confirm)
                    c.applicability_reason = old_c.applicability_reason
                    c.assessed_points = old_c.assessed_points
                else:
                    c.submission_status = 'ns'
                    if old_c.submission_status != 'ns':
                        c.submission_status = 'p'

            except CreditUserSubmission.DoesNotExist:
                continue

        # get all the fields in this credit
        for f in c.get_submission_fields():

            prev_df = f.documentation_field.get_for_creditset(
                old_ss.creditset)

            if prev_df:
                field_class = f.__class__
                if field_class.__name__ == 'TabularSubmissionField':
                    # don't migrate the tabular wrappers, cause they don't actually exist
                    pass
                else:
                    try:
                        prev_cus = CreditUserSubmission.objects.get(credit=prev_df.credit,
                                                                    subcategory_submission__category_submission__submissionset=old_ss)
                        old_f = field_class.objects.get(
                            documentation_field=prev_df,
                            credit_submission=prev_cus)
                        f.value = old_f.value
                        f.save()
                    except field_class.DoesNotExist:
                        pass

        # don't save until all the fields are updated
        c.save()

    try:
        new_boundary = copy.copy(old_ss.boundary)
        new_boundary.submissionset = new_ss
        new_boundary.id = None
        new_boundary.save()
    except Boundary.DoesNotExist:
        pass

    return new_ss
