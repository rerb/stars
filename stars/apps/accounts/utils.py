import MySQLdb
import re

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.template import RequestContext

from stars.apps.institutions.models import StarsAccount, PendingAccount, Institution
from stars.apps.helpers import logger, flashMessage
from django.conf import settings
from django.http import HttpResponseRedirect

logger = logger.getLogger(__name__)


def respond(request, template, context):
    """
        This utility function adds data to the context before sending it
        to the template. The addition is defined by TEMPLATE_CONTEXT_PROCESSORS in
        the settings and calls the function below.
    """

    return render_to_response(template,
                              context,
                              context_instance=RequestContext(request))


def account_context(request):
    """
        This is a custom template-context processor that adds the current user.
    """
    site_status = {'hide_reporting_tool': settings.HIDE_REPORTING_TOOL,
                   'maintenance_mode' : settings.MAINTENANCE_MODE,
                   'broadcast_message' : settings.BROADCAST_MESSAGE,
                  }

    context = {'user': request.user, 'site_status':site_status}
    return context

def tracking_context(request):
    """
        This custom template-context processor adds settings.ANALYTICS_ID
    """
    if settings.ANALYTICS_ID:
        return {'analytics_id': settings.ANALYTICS_ID,}

    return {'analytics_id': None,}

def connect_iss():
    """
        Returns a connection to stars_member_list
    """
    return MySQLdb.connect(user=settings.AASHE_MYSQL_LOGIN, db='iss', passwd=settings.AASHE_MYSQL_PASS, host=settings.AASHE_MYSQL_SERVER)

def change_institution(request, institution):
    """
        Attempts to change the user's current institution - following all the rules, of course!
        This is the ONLY place that a user's current institution should be modified!
        institution is the the institution to select
        Returns True if the institution was changed successfully, False otherwise.
    """
    if request.user.is_authenticated():
        if request.user.is_staff:  # staff are allowed to select any institution
            _update_account_context(request, current_inst=institution)
            return True
        else: # non-staff must have an account to select an institution
            try:
                account = StarsAccount.objects.get(user=request.user, institution=institution)
                _update_account_context(request, account=account)
                return True
            except StarsAccount.DoesNotExist:  # user doesn't have an account for that institution.
                raise PermissionDenied("No such account.")
    else:  # anonymous users may not select any institution
        raise PermissionDenied("You need to log in.")

    return False

def _update_account_context(request, account=None, current_inst=None):
    """
        PACKAGE PRIVATE - this method is intended for use by the AASHE auth package only.
        Other callers should use change_institution() to change the user's account context.
    """
    assert hasattr(request, 'user'), "The AASHE auth requires Django.contrib.auth middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware' above."
    user = request.user

    # this bit of code is here to control presentation logic in the top menu so the correct institution select is shown. Seems a bit hacky?:
    account_list = None
    if user.is_authenticated() and not user.is_staff:  # staff don't have account_lists
        account_list = StarsAccount.objects.filter(user=request.user)
        if account_list.count() <= 1:  # users with only one account don't get an account list either.
            account_list = None

    user.account, user.account_list, user.current_inst = account, account_list, current_inst

    if account and account.user == user:
        account.select()
        user.current_inst = account.institution

        # Confirm that this user has agreed to the Terms of Service even if for another institution
        tos = False
        other_accounts = []
        if account_list:
            for a in account_list:
                if a.terms_of_service:
                    tos = True
                else:
                    other_accounts.append(a)
            if tos: # If they've agreed once, approve them on all StarsAccounts
                for a in other_accounts:
                    a.terms_of_service = True
                    a.save()
        else:
            if user.account.terms_of_service:
                tos = True

        tos_path = "/accounts/tos/"
        if not tos and request.path != tos_path and request.path != "/accounts/logout/" and not re.match("/media/.*", request.path):
            return HttpResponseRedirect("%s?next=%s" % (tos_path, request.path))

    inst_pk = user.current_inst.pk if user.current_inst else None
    request.session['current_inst_pk'] = inst_pk  # store only the Institution id - see ticket #252

    # Add bound methods to user for each permission they have for their current account
    # e.g, user.can_admin, user.can_submit, etc.
    # These allow template code to check for permissions (since templates can't pass parameters)
    for (perm, name) in settings.STARS_PERMISSIONS:
        user.__setattr__("can_%s"%perm,  user.has_perm(perm))
    user.__setattr__('has_tool', user.has_perm('tool'))

    return None


def _get_account_from_session(request):
    """
        PACKAGE PRIVATE - this method is intended for use by the AASHE
        auth middleware ONLY!!

        Clients should access the account context directly from the
        request.user object!

        Return a 2-tuple representing the account:
         - account: current StarsAccount (user-institution) relation, or None
         - current_inst: current selected institution for user
           (because staff don't have accounts), or None
    """
    if not request.user or not request.user.is_authenticated():
        return (None, None)

    # attempt to load Institution from DB based on ID found in session
    # - see ticket #252
    current_inst = None
    inst_pk = request.session.get('current_inst_pk', None)
    if inst_pk:
        try:
            current_inst = Institution.objects.get(pk=inst_pk)
            # @todo - in future, we may want to check here if the
            # institution has been disabled, for non-staff.
        except Institution.DoesNotExist:  # oops - the session's
                                          # institution doesn't exist
                                          # any longer!
            logger.error("Current institution not found in database.")

    if request.user.is_staff: # staff don't have or need accounts to
                              # manage institutions
        if not current_inst: # so, see if the staff member has a
                             # cookie with a current institution from
                             # a previous session
            if request.COOKIES.has_key('current_inst'):
                inst_id = request.COOKIES['current_inst']
                try:
                    current_inst = Institution.objects.get(id=inst_id)
                    # @todo I should really delete the cookie here,
                    # but I can't w/out a Response object
                except Institution.DoesNotExist:
                    flashMessage.send('Current institution not found in db.',
                                      flashMessage.ERROR)
                    logger.error("Current institution not found in database.")
        return (None, current_inst)

    # Convert any pending accounts
    PendingAccount.convert_accounts(request.user)

    account = None
    if current_inst:  # user had an institution selected for this session - ensure its still valid
        try:
            account = StarsAccount.objects.get(user=request.user, institution=current_inst)
        except StarsAccount.DoesNotExist:  # oops - the session institution is no longer valid.
            current_inst = None
    # assert: current_inst is None  or  account.institution.pk == request.session.get('current_inst_pk')

    if not account:  # couldn't get an account from the session - try to find a suitable one in the DB...
        account_list = StarsAccount.objects.filter(user=request.user)
        if account_list.count() == 1: # if there is only one account, we can force the current institution
            account = account_list[0]
        elif account_list.count() > 1: # see if there is an account stored from the user's last session
            account = StarsAccount.get_selected_account(request.user)

    return (account, current_inst)
