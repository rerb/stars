import MySQLdb

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.template import RequestContext

from stars.apps.institutions.models import StarsAccount, Institution

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
    context = {'user': request.user, 'hide_reporting_tool':settings.HIDE_REPORTING_TOOL}
    return context


def connect_aashedata():
    """
        Returns a connection to aashedata01
    """
    return MySQLdb.connect(user='starsapp', db='aashedata01', passwd='J3z4#$szFET--6', host=settings.AASHE_MYSQL_SERVER)


def connect_member_list():
    """
        Returns a connection to stars_member_list
    """
    return MySQLdb.connect(user='starsapp', db='stars_member_list', passwd='J3z4#$szFET--6', host=settings.AASHE_MYSQL_SERVER)


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
            except StarsAccount.DoesNotExist:  # user doesn't have an account for that insitution.
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

    request.session['current_inst'] = user.current_inst
    
    # Add bound methods to user for each permission they have for their current account
    # e.g, user.can_admin, user.can_submit, etc.
    for perm in settings.STARS_PERMISSIONS:
        user.__setattr__("can_%s"%perm,  user.has_perm(perm))


def _get_account_from_session(request):
    """
        PACKAGE PRIVATE - this method is intended for use by the AASHE auth middleware ONLY!!
        Clients should access the account context directly from the request.user object!

        Return a 2-tuple representing the account:
         - account: current StarsAccount (user-institution) relation, or None
         - current_inst: current selected institution for user (because staff don't have accounts), or None
    """  
    if not request.user or not request.user.is_authenticated():
        return (None, None)
    
    current_inst = request.session.get('current_inst', None)

    if request.user.is_staff: # staff don't have or need accounts to manage institutions
        if not current_inst:  # so, see if the staff member has a cookie with a current institution from a previous session
            if request.COOKIES.has_key('current_inst'): 
                aashe_id = request.COOKIES['current_inst']
                current_inst = Institution.load_institution(aashe_id)
        return (None, current_inst)

    account = None
    if current_inst:  # user had an institution selected for this session - ensure its still valid
        try:
            account = StarsAccount.objects.get(user=request.user, institution=current_inst)
        except StarsAccount.DoesNotExist:  # oops - the session institution is no longer valid.
            current_inst = None
    # assert: current_inst is None  or  account.institution == request.session.get('current_inst')
    
    if not account:  # couldn't get an account from the session - try to find a suitable one in the DB...
        account_list = StarsAccount.objects.filter(user=request.user)    
        if account_list.count() == 1: # if there is only one account, we can force the current institution
            account = account_list[0]
        elif account_list.count() > 1: # see if there is an account stored from the user's last session
            account = StarsAccount.get_selected_account(request.user)
        
    return (account, current_inst)
    