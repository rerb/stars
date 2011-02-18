from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.conf import settings

from stars.apps.helpers import flashMessage

from datetime import date

# Class decorators
# Deprecated by Mixins

def staff_decorator(cls):
    class _DecoratedClass(cls):
        def __call__(self, request, *args, **kwargs):
            if request.user.is_staff:
                return super(_DecoratedClass, self).__call__(request, *args, **kwargs)
            elif request.user.is_authenticated():
                raise PermissionDenied("Permission Denied")
            else:
                return _redirect_to_login(request)
    return _DecoratedClass
    
def perm_decorator(perm, error_message=None):
    def decorate(cls):
        class _DecoratedClass(cls):
            def __call__(self, request, *args, **kwargs):
                if request.user.has_perm(perm):
                    return super(_DecoratedClass, self).__call__(request, *args, **kwargs)
                elif request.user.is_authenticated():
                    raise PermissionDenied(error_message if error_message else "Permission Denied")
                else:
                    return _redirect_to_login(request)
        # _DecoratedClass.__bases__=cls.__bases__
        return _DecoratedClass
    return decorate
    
def valid_submission(cls):
    class _DecoratedClass(cls):
        def __call__(self, request, *args, **kwargs):
            problem_with_submission = _get_active_submission_problem_response(request)
            if problem_with_submission:
                return problem_with_submission
            return super(_DecoratedClass, self).__call__(request, *args, **kwargs)
    return _DecoratedClass
    
# Function decorators

def user_is_staff(f):
    """
        This decorator tests to see if the User has staff privileges
    """
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if request.user.is_staff:
            return f(request, *args, **kwargs)            
        elif request.user.is_authenticated(): 
            raise PermissionDenied("AASHE Staff Only")
        else:
            return _redirect_to_login(request)
    return wrap

def user_has_tool(f):
    """
        This decorator tests to see if the User should have access to a tool.
    """
    @wraps(f)
    def wrap(request, *args, **kwargs):
        problem_with_account = _get_account_problem_response(request)
        if problem_with_account:
            return problem_with_account
        if request.user.has_perm('tool'):
            return f(request, *args, **kwargs)            
        elif not request.user.is_authenticated():
            return _redirect_to_login(request)
        else:
            raise PermissionDenied("Access to the tool is restricted.")
    return wrap

def user_is_inst_admin(f):
    """
        This decorator tests to see if the User is administrator of the currently selected institution
        AASHE staff can be admins for all institutions
    """
    @wraps(f)
    def wrap(request, *args, **kwargs):
        problem_with_account = _get_account_problem_response(request)
        if problem_with_account:
            return problem_with_account

        if request.user.has_perm('admin'):
            return f(request, *args, **kwargs)
        else:
            raise PermissionDenied("Admin privileges for %s required."%request.user.current_inst)
    return wrap

def user_can_submit(f):
    """
        This decorator tests to see if the User can submit data for the currently selected institution 
    """
    @wraps(f)
    def wrap(request, *args, **kwargs):
        problem_with_submission = _get_active_submission_problem_response(request)
        if problem_with_submission:
            return problem_with_submission

        if request.user.has_perm('submit'):
            return f(request, *args, **kwargs)
        else:
            raise PermissionDenied("Privilege to submit data for %s required."%request.user.current_inst)
    return wrap

def user_can_view(f):
    """
        This decorator tests to see if the User can view un-rated submission data for the currently selected institution 
    """
    @wraps(f)
    def wrap(request, *args, **kwargs):
        problem_with_submission = _get_active_submission_problem_response(request)
        if problem_with_submission:
            return problem_with_submission

        if request.user.has_perm('view'):
            return f(request, *args, **kwargs)
        else:
            raise PermissionDenied("Privilege to view data for %s required."%request.user.current_inst)
    return wrap

def _get_account_problem_response(request):
    """ Returns a response if there are any problems with the user's account, None otherwise """
    if not request.user.is_authenticated():
        return _redirect_to_login(request)

    current_inst = request.user.current_inst

    if request.user.is_staff and not current_inst:
        flashMessage.send("You need to select an institution.", flashMessage.NOTICE)
        path = urlquote(request.get_full_path())
        return HttpResponseRedirect('%s?next=%s' %(settings.ADMIN_URL, path))

    if not current_inst:
        if request.user.account_list: # user has accounts, just none selected (this shouldn't happen, but just in case...)
            return _redirect_to_tool(request, "You need to select an institution before proceeding")
        else: # user has no accounts (also shouldn't really happen...
            error_msg = """Your AASHE Account is not verified to access the STARS Reporting Tool.  Only institutions that are registered as STARS Participants are able to access the Reporting Tool.  You may be receiving this message because you have not been listed as a user by the account's administrator.  The administrator is likely to be the person who first registered for STARS or your institution's STARS Liaison.  Please contact this person so they may list you as a user in the Reporting Tool and you may gain access.  
<br/><br/>
To add users, once the administrator is logged into the Reporting Tool, simply choose the "Manage Institution" link and click on the "Users" tab."""
            raise PermissionDenied(error_msg)
    else:
        if not current_inst.enabled:
            raise PermissionDenied("This institution is not enabled.")
            
    # assert user has a valid account with their current institution
    return None

def _get_active_submission_problem_response(request):
    """ 
        Returns an error response if there are any problems with the user's active submission, None otherwise
        
        NOTE: this is gradually being replaced by the mixin in `stars.apps.auth.mixins`.
        Any changes made here, should be duplicated there.
    """
    problem_with_account = _get_account_problem_response(request)
    if problem_with_account:
       return problem_with_account 
    
    # assert user.is_authenticated() and has a valid instititution selected
    current_inst = request.user.current_inst
    active_submission = current_inst.get_active_submission()
                
    if not active_submission:
        if request.user.is_staff:
            flashMessage.send("You need to create an active submission for %s."%current_inst, flashMessage.NOTICE)
            return HttpResponseRedirect(settings.MANAGE_SUBMISSION_SETS_URL)
        if request.user.account.has_perm('admin'):
            flashMessage.send("You need to select or purchase an active submission for %s."%current_inst, flashMessage.NOTICE)
            return HttpResponseRedirect(settings.MANAGE_SUBMISSION_SETS_URL)
        else:
            raise PermissionDenied("%s has no active submissions."%current_inst)
    elif active_submission.is_locked:
        raise PermissionDenied("This submission has been locked. This could be because you are migrating to a more recent Credit Set. Please contact your STARS Liaison or the STARS Team if you have any questions.")
    elif active_submission.status != 'ps' and not request.user.is_staff:
        raise PermissionDenied("This submission has been submitted and is no longer available for editing. See it under 'My Report(s).'")
    elif active_submission.missed_deadline():
        raise PermissionDenied("The submission deadline for this submission has passed. It is no longer available to edit.")
    else:
        if not active_submission.is_enabled():
            raise PermissionDenied("This submission hasn't been enabled. It will be available once AASHE receives payment.")
 
    assert active_submission
    return None
    
    
def _redirect_to_login(request):
    """ Returns a Redirect Response to the login URL, with a ?next= parameter back to the current request path """
    flashMessage.send("Please login to access STARS tools.", flashMessage.NOTICE)
    path = urlquote(request.get_full_path())
    return HttpResponseRedirect('%s?next=%s' %(settings.LOGIN_URL, path))

def _redirect_to_tool(request, message):
    """ Returns a Redirect Response to the STARS tool, showing the given message """
    flashMessage.send(message, flashMessage.NOTICE)
    return HttpResponseRedirect(settings.DASHBOARD_URL)

    
