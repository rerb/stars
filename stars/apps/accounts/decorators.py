from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
#
#from stars.apps.institutions.models import Institution
#
## Class decorators
## Deprecated by Mixins
#
#def staff_decorator(cls):
#    class _DecoratedClass(cls):
#        def __call__(self, request, *args, **kwargs):
#            if request.user.is_staff:
#                return super(_DecoratedClass, self).__call__(request, *args, **kwargs)
#            elif request.user.is_authenticated():
#                raise PermissionDenied("Permission Denied")
#            else:
#                return _redirect_to_login(request)
#    return _DecoratedClass
#
#def perm_decorator(perm, error_message=None):
#    def decorate(cls):
#        class _DecoratedClass(cls):
#            def __call__(self, request, *args, **kwargs):
#                if request.user.has_perm(perm):
#                    return super(_DecoratedClass, self).__call__(request, *args, **kwargs)
#                elif request.user.is_authenticated():
#                    raise PermissionDenied(error_message if error_message else "Permission Denied")
#                else:
#                    return _redirect_to_login(request)
#        # _DecoratedClass.__bases__=cls.__bases__
#        return _DecoratedClass
#    return decorate
#
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
#
#def inst_is_member(f):
#    """
#        Tests against ISS for the institution's membership
#    """
#    @wraps(f)
#    def wrap(request, *args, **kwargs):
#        if request.user.get_profile().is_member:
#            return f(request, *args, **kwargs)
#        elif not request.user.is_authenticated():
#            return _redirect_to_login(request)
#        else:
#            raise PermissionDenied("Access is restricted to AASHE Members Only.")
#    return wrap
#
#def inst_is_participant(f):
#    """
#        Tests against ISS for the institution's participation in STARS
#    """
#    @wraps(f)
#    def wrap(request, *args, **kwargs):
#        if request.user.get_profile().is_participant():
#            return f(request, *args, **kwargs)
#        if not request.user.is_authenticated():
#            return _redirect_to_login(request)
#        else:
#            raise PermissionDenied("Access is restricted to STARS Participants Only.")
#    return wrap
#
#def user_has_tool(f):
#    """
#        This decorator tests to see if the User should have access to a tool.
#    """
#    @wraps(f)
#    def wrap(request, *args, **kwargs):
#        problem_with_account = _get_account_problem_response(
#            request=request,
#            institution_slug=kwargs['institution_slug'])
#        if problem_with_account:
#            return problem_with_account
#        if request.user.has_perm('tool'):
#            return f(request, *args, **kwargs)
#        elif not request.user.is_authenticated():
#            return _redirect_to_login(request)
#        else:
#            raise PermissionDenied("Access to the tool is restricted.")
#    return wrap
#
#def _get_account_problem_response(request, institution_slug):
#    """ Returns a response if there are any problems with the user's
#    account, None otherwise """
#
#    if not request.user.is_authenticated():
#        return _redirect_to_login(request)
#
#    try:
#        current_inst = Institution.objects.get(slug=institution_slug)
#    except Institution.DoesNotExist:
#        current_inst = None
#
#    if request.user.is_staff and not current_inst:
#        messages.info(request, "You need to select an institution.")
#        path = urlquote(request.get_full_path())
#        return HttpResponseRedirect('%s?next=%s' %(settings.ADMIN_URL, path))
#
#    if not current_inst:
#        if request.user.account_list: # user has accounts, just none
#                                      # selected (this shouldn't
#                                      # happen, but just in case...)
#            return _redirect_to_tool(request,
#                                     "You need to select an institution "
#                                     "before proceeding")
#        else: # user has no accounts (also shouldn't really happen...
#
#            error_msg = """
#            Your AASHE Account is not verified to access the STARS
#            Reporting Tool.  Only institutions that are registered as
#            STARS Participants are able to access the Reporting Tool.
#            You may be receiving this message because you have not
#            been listed as a user by the account's administrator.  The
#            administrator is likely to be the person who first
#            registered for STARS or your institution's STARS Liaison.
#            Please contact this person so they may list you as a user
#            in the Reporting Tool and you may gain access.
#
#            <br/><br/>
#
#            To add users, once the administrator is logged into the
#            Reporting Tool, simply choose the "Manage Institution"
#            link and click on the "Users" tab."""
#
#            raise PermissionDenied(error_msg)
#    else:
#        if not current_inst.enabled:
#            raise PermissionDenied("This institution is not enabled.")
#
#    # assert user has a valid account with their current institution
#    return None
#
def _redirect_to_login(request):
    """ Returns a Redirect Response to the login URL, with a ?next=
    parameter back to the current request path """
    messages.info(request, "Please login to access STARS tools.")
    path = urlquote(request.get_full_path())
    return HttpResponseRedirect('%s?next=%s' %(settings.LOGIN_URL, path))
#
#def _redirect_to_tool(request, message):
#    """ Returns a Redirect Response to the STARS tool, showing the
#    given message """
#    messages.info(request, message)
#    return HttpResponseRedirect(settings.DASHBOARD_URL)
