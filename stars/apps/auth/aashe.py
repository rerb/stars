from django.conf import settings
from django.contrib.auth.models import User, check_password

from stars.apps.auth import xml_rpc
from stars.apps.helpers import watchdog

import xmlrpclib, md5, random, hashlib, hmac
from time import time

# Django Docs:
# http://docs.djangoproject.com/en/dev/topics/auth/

class AASHEAuthBackend:
    """
        Authenticate against the Drupal AASHE account system
    """
    def authenticate(self, username=None, password=None):
        
        # authenticate with drupal
        user_dict = xml_rpc.login(username, password)
        
        # if the user doesn't exist in django, create it
        # Authentication doesn't actually give them access to their school's submissions
        # they have to be given privileges by their administrator
        
        if user_dict:
            user = xml_rpc.get_user_from_user_dict(user_dict['user'], user_dict['sessid'])
            # don't allow non-staff to login during maintenance mode.
            if settings.MAINTENANCE_MODE and not user.is_staff:
                return None
            else:
                return user
            
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
       
    def has_perm(self, user, perm):
        """ 
            Return True if the user has the given permission 
            Backend hook.  Call is routed via contrib.auth.user.has_perm
            AASHE Permissions apply to the user's currently selected account
            - thus, we can't user the Django permission system, which applies permissions to content_types only
        """
        if not user or not user.is_authenticated:
            return False    # anonymous users have no permissions
        
        if user.is_staff:
            return True     # staff users have all permissions

        if settings.HIDE_REPORTING_TOOL:  # if the site is hidden, no access to any parts that require permissions
            return False
        
        if not user.account:
            return False    # only users with an account selected have permissions
        
        if perm == 'dashboard':  # every role has access to a dashboard...
            for perm in settings.STARS_PERMISSIONS:
                if user.account.has_perm(perm):
                    return True
            # assert: user has no role assigned to their current account
            return False
        
        if not perm in settings.STARS_PERMISSIONS:
            watchdog.log('Auth', 'Internal Error: Attempt to check non-exisitent permission %s'%perm, watchdog.ERROR)
            return False    #  can't give permission for something we don't recognize!
        
        return user.account.has_perm(perm)
    