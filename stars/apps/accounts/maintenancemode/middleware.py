from django.conf import settings
from django.http import HttpResponseRedirect

from stars.apps.auth.maintenancemode.views import temporary_unavailable

class MaintenanceModeMiddleware(object):
    """
        Maintenance Mode Middleware is based on django-maintenancemode: http://code.google.com/p/django-maintenancemode/
        But with simplified (less generic) code and additional features to make it work like Drupal's offline mode.
        Relies on settings.MAINTENANCE_MODE - if True, non-staff users are redirected to the custom 503 page.
    """
    def process_request(self, request):
        # Allow access if middleware is not activated
        if not settings.MAINTENANCE_MODE:
            return None

        # Allow access if remote ip is in INTERNAL_IPS
        if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return None
        
        # Allow access to media and other static files (only relevant for Django test server)
        if request.path.startswith(settings.MEDIA_URL):
            return None
        
        # Allow access to the login and logout pages.
        if request.path == settings.LOGIN_URL or request.path == settings.LOGOUT_URL:
            return None
        
        # Allow access to staff, logout any others.
        if hasattr(request, 'user'):
            if request.user.is_staff:
                return None
            elif request.user.is_authenticated():
                return HttpResponseRedirect(settings.LOGOUT_URL)
        
        # Otherwise show the user the 503 page
        return temporary_unavailable(request)
