import aashe_rules
import sys

from datetime import datetime

from stars.apps.institutions.models import StarsAccount

def user_has_access_level(user, access_level, institution):
    if user.is_staff:
        return True
    try:
        account = StarsAccount.objects.get(institution=institution, user=user)
        if account.has_access_level(access_level):
            return True
    except StarsAccount.DoesNotExist:
        pass
    return False
aashe_rules.site.register("user_has_access_level", user_has_access_level)

def institution_can_get_rated(institution):
    if institution.is_participant and institution.current_subscription.get_available_ratings() > 0 and institution.current_subscription.paid_in_full:
    	return True
    return False
aashe_rules.site.register("institution_can_get_rated", institution_can_get_rated)

def institution_has_score_feature(institution):
    return institution.is_participant
aashe_rules.site.register("institution_has_score_feature", institution_has_score_feature)

def institution_has_internal_notes_feature(institution):
    return institution.is_participant
aashe_rules.site.register("institution_has_internal_notes_feature", institution_has_internal_notes_feature)

def institution_has_my_resources(institution):
    return institution.is_participant
aashe_rules.site.register("institution_has_my_resources", institution_has_my_resources)

def institution_has_export(institution):
    return institution.is_participant
aashe_rules.site.register("institution_has_export", institution_has_export)

def isntitution_has_my_reports(institution):
    return institution.is_participant
aashe_rules.site.register("isntitution_has_my_reports", isntitution_has_my_reports)

def institution_has_snapshot_feature(institution):
    return institution.current_submission.creditset.has_feature('snapshot')
aashe_rules.site.register("institution_has_snapshot_feature", institution_has_snapshot_feature)