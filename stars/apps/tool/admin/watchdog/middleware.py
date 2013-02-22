from django.conf import settings
from django.shortcuts import render_to_response
from django.http import Http404
from django.core.exceptions import PermissionDenied

from stars.apps.tool.admin.watchdog.models import WatchdogEntry
from stars.apps.helpers import watchdog
from stars.apps.helpers.shortcuts import render_to_any_response
from stars.apps.helpers.views import forbidden

class WatchdogMiddleware :
    """
    Provides middleware services for error logging and handling
    """
    def process_request(self, request) :
        """
        Called before the request is processed.
        Stores information about the request in case its needed by watchdog
        Could use process_view to get view info as well, but then we don't log the request if there is an error before process_view is called...
        """
        WatchdogEntry.set_request(request, None)  
        # Always return None so that request continues to be processed normally!
        return None
    
    def process_response(self, request, response):
        """
        Log any Page Not Found and Permission Denied responses, just for reference.
        """
        if (response.status_code == 404):
            watchdog.log("404", "Page Not Found", watchdog.NOTICE)
        if (response.status_code == 403):
            watchdog.log("403", "Permission Denied", watchdog.NOTICE)
        return response
        
    def process_exception(self, request, exception) :
        """
         Logs any unhandled exception as an Error, except 403's & 404's, which are trapped above. 
         Also, acts as a handler for 403's, creating a custom response.
        """
        if isinstance(exception, PermissionDenied):
            return forbidden(request, exception.__str__())
        if ( not isinstance(exception, Http404) ):
            watchdog.log_exception(exception)
            
        return None
