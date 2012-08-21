from logging import getLogger

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
from stars.apps.accounts.utils import change_institution
from stars.apps.accounts.forms import LoginForm, TOSForm
from stars.apps.accounts.utils import respond

logger = getLogger('stars.request')

@never_cache
def login(request, redirect_field_name=REDIRECT_FIELD_NAME):
    """"
        Displays the login form and handles the login action.
        Copied directly from django.contrib.auth.views.login, but uses LoginForm instead of AuthenticationForm
        Hoping http://code.djangoproject.com/ticket/8274 gets resolved and we can use the built-in function
    """
    template_name = 'auth/login.html'
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.user.is_authenticated() and redirect_to != '':
        return HttpResponseRedirect(redirect_to)
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
            logger.info("Attempt to select non-existent institution id = %s" %
                        institution_id, extra={'request': request})
        if change_institution(request, institution):
            return HttpResponseRedirect(settings.DASHBOARD_URL)
        else:
            raise PermissionDenied("Your request could not be completed.")
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)


def terms_of_service(request):
    """
        Provide a form where a user can agree to the terms of service
    """

    if not request.user.account:
        logger.error("User passed to TOS w/out StarsAccount: uid",
                     extra={'request': request})
        return HttpResponseRedirect("/")

    next = request.REQUEST.get('next', '/')

    form = TOSForm(instance=request.user.account)
    if request.method == "POST":
        form = TOSForm(request.POST, instance=request.user.account)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(next)

    return respond(request, "auth/tos_agree.html", {'form': form, 'next': next,})
