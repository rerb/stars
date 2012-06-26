from stars.apps.accounts.utils import _get_account_from_session, _update_account_context

"""
    AASHE Authentication Backend Middleware
    Loads account information and permission attributes into the request.user object:
      - account: the user's current StarsAccount object (may be None!!  esp. for staff)
      - account_list: a list of the user's valid StarsAcccounts, or None if they have only 1 or fewer (or are staff!!)
      - current_inst: same as account.institution, but needed for staff, who may not have an instutiton
      - can_admin, can_submit, etc...  one such attribute for each settings.STARS_PERMISSIONS
      
    This Middleware must be installed AFTER the Django.contrib.auth middleware in settings.
"""
class AuthenticationMiddleware(object):
    def process_request(self, request):
        """ Add the user's account context to the user object in the request """
        # since the user object is stored in the session, this information may already be in the request.
        # however, load it again in case the user's accounts have changed since their last request.
        return _update_account_context(request, *_get_account_from_session(request))
