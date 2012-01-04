import aashe_rules
import sys
from stars.apps.institutions.models import StarsAccount

from datetime import datetime

def submission_is_editable(submission):
    return submission.status != 'r' and submission.submission_deadline > datetime.now()
aashe_rules.site.register("submission_is_editable", submission_is_editable)

def user_can_edit_submission(user, submission):
    if submission_is_editable(submission):
        try:
            account = StarsAccount.objects.get(institution=submission.institution, user=user)
            if account.has_access_level('submit'):
                return True
        except StarsAccount.DoesNotExist:
            pass
    return False
aashe_rules.site.register("user_can_edit_submission", user_can_edit_submission)

def user_can_manage_submission(user, submission):
    if submission_is_editable(submission):
        try:
            account = StarsAccount.objects.get(institution=submission.institution, user=user)
            if account.has_access_level('admin'):
                return True
        except StarsAccount.DoesNotExist:
            pass
    return False
aashe_rules.site.register("user_can_manage_submission", user_can_manage_submission)
