import aashe_rules

from stars.apps.credits.models import CreditSet
from stars.apps.institutions.rules import (institution_can_get_rated,
                                           institution_has_export,
                                           institution_has_snapshot_feature,
                                           user_has_access_level)


def submission_is_editable(submission):
    """
        A submission is only editable if it is the current submission
        for the institution and isn't rated (just a check for now)
    """
    return (submission.status != 'r' and
            submission == submission.institution.current_submission)

aashe_rules.site.register("submission_is_editable", submission_is_editable)

def submission_is_not_locked(submission):
    """
        Exposes SubmissionSet.is_locked.
    """
    return not submission.is_locked

aashe_rules.site.register("submission_is_not_locked", submission_is_not_locked)

def publish_credit_data(credit_submission):
    """
        Identifies whether a credit's fields should be published anywhere
    """
    return credit_submission.submission_status == 'c'

def user_can_preview_submission(user, submission):
    """
        Only rated submissions and the current submission data
    """
    if user_has_access_level(user, 'view', submission.institution):
        if (submission.status == 'r' or
            submission == submission.institution.current_submission):
            return True
    return False

aashe_rules.site.register("user_can_preview_submission",
                          user_can_preview_submission)

def user_can_view_submission(user, submission):
    """
        If a submission isn't rated then only the institution's users
        can see the submission
    """
    if submission.status == 'r':
        return True
    return user_can_preview_submission(user, submission)

aashe_rules.site.register("user_can_view_submission", user_can_view_submission)

def user_can_view_pdf(user, submission):
    if (not institution_has_export(submission.institution) and
        submission.status != 'r'):
        return False
    return True

aashe_rules.site.register("user_can_view_pdf", user_can_view_pdf)

def user_can_edit_submission(user, submission):
    return (submission_is_editable(submission) and
            user_has_access_level(user, 'submit', submission.institution))

aashe_rules.site.register("user_can_edit_submission", user_can_edit_submission)

def user_can_manage_submission(user, submission):
    return (submission_is_editable(submission) and
            user_has_access_level(user, 'admin', submission.institution))

aashe_rules.site.register("user_can_manage_submission",
                          user_can_manage_submission)

def user_can_see_internal_notes(user, submission):
    return user_has_access_level(user, 'view', submission.institution)

aashe_rules.site.register("user_can_see_internal_notes",
                          user_can_see_internal_notes)

def user_can_submit_for_rating(user, submission):
    """
        Rule defines whether a user (and institution) has
        privileges to submit a SubmissionSet for a rating
    """
    return (user_can_manage_submission(user, submission) and
            institution_can_get_rated(submission.institution))

aashe_rules.site.register("user_can_submit_for_rating",
                          user_can_submit_for_rating)

def user_can_submit_snapshot(user, submission):
    return (user_can_manage_submission(user, submission) and
            institution_has_snapshot_feature(submission.institution))

aashe_rules.site.register("user_can_submit_snapshot", user_can_submit_snapshot)

def user_can_migrate_version(user, institution):
    """
        Only institution admins can migrate a submission
    """
    if (institution.current_submission.creditset.version !=
        CreditSet.objects.get_latest().version):
        return user_has_access_level(user, 'admin', institution)
    else:
        return False

aashe_rules.site.register("user_can_migrate_version", user_can_migrate_version)

def user_can_migrate_data(user, institution):
    """
        Can this user do a data migration?
        Only institution admins can migrate a submission
    """
    return user_has_access_level(user, 'admin', institution)

aashe_rules.site.register("user_can_migrate_data", user_can_migrate_data)

def user_can_migrate_from_submission(user, submission):
    """
        Only institution admins can migrate a submission

        Participants can migrate from Reports or Snapshots
        Respondents can only migrate from Reports
    """
    if user_has_access_level(user, 'admin', submission.institution):
        if submission.institution.is_participant:
            if submission.status == 'r' or submission.status == 'f':
                return True
        else:
            if submission.status == 'r':
                return True
    return False
aashe_rules.site.register("user_can_migrate_from_submission",
                          user_can_migrate_from_submission)

def submission_has_scores(submission):
    """
        Indicates that the preview or reporting tool should show scores for
        this submission
    """
    if submission.status == 'r':
        return submission.rating.name != "Reporter"
    elif submission.status == 'f':
        # don't show score for snapshots
        return False
    else:
        return submission.institution.is_participant

aashe_rules.site.register("submission_has_scores", submission_has_scores)
