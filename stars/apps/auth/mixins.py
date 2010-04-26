from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.conf import settings

from stars.apps.helpers import flashMessage

class StarsMixin(object):
    """
        The base mixin class that provides `redirect_to_login` for now... maybe others
    """
    
    def redirect_to_login(self, request):
        """ Returns a Redirect Response to the login URL, with a ?next= parameter back to the current request path """
        flashMessage.send("Please login to access STARS tools.", flashMessage.NOTICE)
        path = urlquote(request.get_full_path())
        return HttpResponseRedirect('%s?next=%s' %(settings.LOGIN_URL, path))

    def redirect_to_tool(self, request, message):
        """ Returns a Redirect Response to the STARS tool, showing the given message """
        flashMessage.send(message, flashMessage.NOTICE)
        return HttpResponseRedirect(settings.DASHBOARD_URL)

class AuthenticatedMixin(StarsMixin):
    """
        This class should be used as a Class-based view mixin to ensure that a user is logged in
    """
    def __call__(self, request, *args, **kwargs):
        """
            Makes sure the current user is authenticated before executing `__call__`
            
            Subclasses can define any of the following:
                
                `auth_mixin_redirect`: if this is defined unauthenticated users will be forwarded to this url
                
                or
                
                `auth_mixin_template`: if this is defined (and `auth_redirect` is not) `__call__` will
                    render to the template with `auth_mixin_context` if it's defined
                `auth_mixin_context`: a dictionary of context variables for `auth_mixin_template`
        """
        if not request.user.is_authenticated():
            if hasattr(self, 'auth_mixin_redirect'):
                return HttpResponseRedirect(self.auth_redirect)
            elif hasattr(self, 'auth_mixin_template'):
                context = getattr(self, 'auth_mixin_context', {})
                return respond(request, self.auth_mixin_template, context)
            else:
                return self.redirect_to_login(request)
        
        return super(AuthenticatedMixin, self).__call__(request, *args, **kwargs)

class AccountMixin(StarsMixin):
    """
        This class should be used as a mixin to provide the subclass with `STARSAccount` verification.

        Example:
        class MyClass(AccountMixin, BaseClass):
           pass

        If there is an issue with the submissin `__call__` will report the error with a Response object
        or an exception.
        
        Assumes `__call__` returns a response object and has the following declaration:
            def __call__(self, request, *args, **kwargs):
                
        @Todo: check for expired submissionsets!
    """
    
    def __call__(self, request, *args, **kwargs):
        
        result = self.get_account_problem_response(request)
        if result:
            return result
        
        return super(AccountMixin, self).__call__(request, *args, **kwargs)
    
    def get_account_problem_response(self, request):
        """
            Detects any problems with the user/institution's accounts including:
                - no current institution
                - current institution isn't enabled
                
            Assumes:
                - apps.auth.middleware is adding the following properties to `request.user`:
                    - `current_inst`
                    - `account_list`
                
            NOTE: this is a duplicate of the decorator in `stars.apps.auth.decorators`.
            Any changes made here, should be duplicated there.
        """
        
        current_inst = request.user.current_inst
        
        if not current_inst:
            
            if request.user.is_staff:
                flashMessage.send("You need to select an institution.", flashMessage.NOTICE)
                path = urlquote(request.get_full_path())
                return HttpResponseRedirect('%s?next=%s' %(settings.ADMIN_URL, path))
                
            elif request.user.account_list: # user has accounts, just none selected (this shouldn't happen, but just in case...)
                return self.redirect_to_tool(request, "You need to select an institution before proceeding")
            else: # user has no accounts (also shouldn't really happen...
                error_msg = """Your AASHE Account is not verified to access the STARS Reporting Tool.  Only institutions that are registered as STARS Participants are able to access the Reporting Tool.  You may be receiving this message because you have not been listed as a user by the account's administrator.  The administrator is likely to be the person who first registered for STARS or your institution's STARS Liaison.  Please contact this person so they may list you as a user in the Reporting Tool and you may gain access.  
    <br/><br/>
    To add users, once the administrator is logged into the Reporting Tool, simply choose the "Manage Institution" link and click on the "Users" tab."""
                raise PermissionDenied(error_msg)
        else:
            if not current_inst.enabled:
                raise PermissionDenied("This institution is not enabled.")
                
        return None
        
class SubmissionMixin(AccountMixin):
    """
        This class should be used as a mixin to provide the subclass with STARS submission verification.

        Example:
        class MyClass(SubmissionMixin, BaseClass):
           pass

        If there is an issue with the submissin `__call__` will report the error with a Response object
        or an exception.
        
        Assumes `__call__` returns a response object and has the following declaration:
            def __call__(self, request, *args, **kwargs):
    """
    
    def __call__(self, request, *args, **kwargs):
        
        result = self.get_account_problem_response(request)
        if result:
            return result
        result = self.get_active_submission_problem_response(request)
        if result:
            return result
        
        return super(SubmissionMixin, self).__call__(request, *args, **kwargs)
    
    def get_active_submission_problem_response(self, request):
        """
            Detects any problems with the institution's submissionset including:
                - no active submission
                - active submission hasn't been enabled
                
            Assumes:
                - apps.auth.middleware is adding the following properties to `request.user`:
                    - `current_inst`
                    
            NOTE: this is a duplicate of the decorator in `stars.apps.auth.decorators`.
            Any changes made here, should be duplicated there.
        """
        
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
        else:
            if not active_submission.is_enabled():
                raise PermissionDenied("This submission hasn't been enabled. It will be available once AASHE receives payment.")

        return None

class PermMixin(StarsMixin):
    """
        This class should be used as a mixin to provide the subclass with permission-based access.
        The extending class should define a `perm_list` property list of permissions
        required to call the class.

        Example:
        class MyClass(PermMixin, BaseClass):
           perm_list = ['admin',]
   
        If `perm_list` is empty or undefined `__call__` will raise a `PermissionDenied` exception
        and if `perm_message` is defined it will use that as the error message.

        If the user is not authenticated `__call__` will return an HttpRedirect to the login path.
        
        Assumes `__call__` returns a response object and has the following declaration:
            def __call__(self, request, *args, **kwargs):
    """
   
    def __call__(self, request, *args, **kwargs):
        
        has_perms = True
        
        # Unauthenticated users are redirected to Login
        if not request.user.is_authenticated():
            return self.redirect_to_login(request)
        else:
            _perm_list = []
            if hasattr(self, 'perm_list'):
                _perm_list += self.perm_list
            else:
                has_perms = False
            
            # Test all the required permissions
            for perm in _perm_list:
                if not request.user.has_perm(perm):
                    has_perms = False
                    
        if has_perms:
            return super(PermMixin, self).__call__(request, *args, **kwargs)
        else:
            raise PermissionDenied(self.perm_message if hasattr(self, 'perm_message') else "Permission Denied")