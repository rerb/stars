from logging import getLogger
import xmlrpclib, random, hashlib, hmac
from time import time

from django.conf import settings
from django.contrib.auth.models import User, check_password

from stars.apps.accounts import xml_rpc
from stars.apps.institutions.models import StarsAccount

# Django Docs:
# http://docs.djangoproject.com/en/dev/topics/auth/

logger = getLogger('stars.user')


class AASHEAuthBackend:
    """
        Authenticate against the Drupal AASHE account system
    """
    supports_anonymous_user = True
    supports_object_permissions = False

    def authenticate(self, username=None, password=None):

        # authenticate with drupal
        user_dict = xml_rpc.login(username, password)

        # if the user doesn't exist in django, create it
        # Authentication doesn't actually give them access to their
        # school's submissions they have to be given privileges by
        # their administrator

        if user_dict:
            user = xml_rpc.get_user_from_user_dict(user_dict['user'],
                                                   user_dict['sessid'])
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def has_perm(self, user, perm):
        """
            Return True if the user has the given permission Backend
            hook.  Call is routed via contrib.auth.user.has_perm AASHE
            Permissions apply to the user's currently selected account
            - thus, we can't user the Django permission system, which
            applies permissions to content_types only
        """
        if not user or not user.is_authenticated:
            return False    # anonymous users have no permissions

        if user.is_staff:
            return True     # staff users have all permissions

        if settings.HIDE_REPORTING_TOOL:  # if the site is hidden, no
                                          # access to any parts that
                                          # require permissions
            return False

        if not hasattr(user, 'account') or not user.account:
            return False    # only users with an account selected have
                            # permissions

        # Permission can optionally have a specific institution
        # associated, as in: perm:## where ## is the institution's id
        # to check permissions on.
        perm, sep, inst_id = perm.partition(':')
        if inst_id:  # Does user have any permissions with the institution?
            try:
                account = StarsAccount.objects.get(user=user,
                                                   institution__id=inst_id)
            except StarsAccount.DoesNotExist:  # user has no accounts,
                                               # so no permissions with
                                                #this institution.
                return False
        else:  # if no explicit institution id given, use users current account.
            account = user.account

        PERMS = [x for (x,y) in settings.STARS_PERMISSIONS]

        if perm == 'any' or perm == 'tool':  # every role has access
                                             # to the reporting tool...
            for perm in PERMS:
                if account.has_perm(perm):
                    return True
            # assert: user has no role assigned to their current account
            return False

        if not perm in PERMS:
            logger.error('Internal Error: Attempt to check non-exisitent '
                         'permission %s' % perm, extra={'user': user})
            return False    # can't give permission for something we
                            # don't recognize!

        return account.has_perm(perm)
