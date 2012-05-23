import aashe_rules
import sys
from stars.apps.institutions.rules import institution_can_get_rated, user_has_access_level, institution_has_snapshot_feature
from stars.apps.credits.models import CreditSet

from datetime import datetime

def submission_is_editable(submission):
    """
        A submission is only editable if it is the current submission
        for the institution and isn't rated (just a check for now)
    """
    return submission.status != 'r' and submission == submission.institution.current_submission
aashe_rules.site.register("submission_is_editable", submission_is_editable)

def user_can_preview_submission(user, submission):
    return user_has_access_level(user, 'view', submission.institution)
aashe_rules.site.register("user_can_preview_submission", user_can_preview_submission)

def user_can_edit_submission(user, submission):
    return submission_is_editable(submission) and user_has_access_level(user, 'submit', submission.institution)
aashe_rules.site.register("user_can_edit_submission", user_can_edit_submission)

def user_can_manage_submission(user, submission):
    return submission_is_editable(submission) and user_has_access_level(user, 'admin', submission.institution)
aashe_rules.site.register("user_can_manage_submission", user_can_manage_submission)

def user_can_see_internal_notes(user, submission):
    return user_has_access_level(user, 'view', submission.institution)
aashe_rules.site.register("user_can_see_internal_notes", user_can_see_internal_notes)

def user_can_submit_for_rating(user, submission):
    """
        Rule defines whether a user (and institution) has
        privileges to submit a SubmissionSet for a rating 
    """
    return user_can_manage_submission(user, submission) and institution_can_get_rated(submission.institution)
aashe_rules.site.register("user_can_submit_for_rating", user_can_submit_for_rating)

def user_can_submit_snapshot(user, submission):
    return user_can_manage_submission(user, submission) and institution_has_snapshot_feature(submission.institution)
aashe_rules.site.register("user_can_submit_snapshot", user_can_submit_snapshot)

def user_can_migrate_submission(user, submission):
    """
        Only institution admins can migrate a submission
    """
    if submission.creditset.version != CreditSet.objects.get_latest().version:
        return user_has_access_level(user, 'admin', submission.institution)
    else:
        return False
aashe_rules.site.register("user_can_migrate_submission", user_can_migrate_submission)

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
    