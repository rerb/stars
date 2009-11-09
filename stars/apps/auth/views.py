from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.decorators.cache import never_cache
from django.contrib.sites.models import Site, RequestSite
from django.shortcuts import render_to_response
from django.template import RequestContext

from stars.apps.institutions.models import Institution
from stars.apps.auth.utils import change_institution
from stars.apps.helpers import watchdog
from stars.apps.auth.forms import LoginForm
from stars.apps.auth.decorators import user_can_submit

@never_cache
def login(request, redirect_field_name=REDIRECT_FIELD_NAME):
    """"
        Displays the login form and handles the login action.
        Copied directly from django.contrib.auth.views.login, but uses LoginForm instead of AuthenticationForm
        Hoping http://code.djangoproject.com/ticket/8274 gets resolved and we can use the built-in function
    """
    template_name = 'auth/login.html'
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            from django.contrib.auth import login
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return HttpResponseRedirect(redirect_to)
    else:
        form = LoginForm(request)
    request.session.set_test_cookie()
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)
    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))


def select_school(request, institution_id):
    """
        This view updates the session to reflect the selected institution
    """
    if request.user.is_authenticated():
        institution = None
        try:
            institution = Institution.objects.get(id=institution_id)
        except Institution.DoesNotExist:
            watchdog.log('Auth', "Attempt to select non-existent institution id= %s"%institution_id, watchdog.NOTICE)
              
        if change_institution(request, institution):
            return HttpResponseRedirect(settings.DASHBOARD_URL)
        else:
            raise PermissionDenied("Your request could not be completed.")
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)

@user_can_submit
def serve_uploaded_file(request, inst_id, creditset_id, credit_id, field_id, filename):
    """
        Serves files after authentication
    """
    current_inst = request.user.current_inst
    if not current_inst or current_inst.id != int(inst_id):
        raise PermissionDenied("File not found")
        
    stored_path = "secure/%s/%s/%s/%s/%s" % (inst_id, creditset_id, credit_id, field_id, filename) 
    
    from django.views.static import serve
    return serve(request, stored_path, document_root=settings.MEDIA_ROOT)
    