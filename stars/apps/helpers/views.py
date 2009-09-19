from django.template import RequestContext
from django.http import HttpResponseServerError, HttpResponseForbidden

from stars.apps.helpers.shortcuts import render_to_any_response
from stars.apps.helpers import exceptions
from stars.apps.dashboard.admin.watchdog.models import WatchdogEntry

def server_error(request):
    context = {}
    
    if (WatchdogEntry.exception):
        if ( isinstance(WatchdogEntry.exception, exceptions.StarsException) ) :
            user_message = WatchdogEntry.exception.user_message
        else:
            user_message = ""
        context = { "user_message":user_message, 
                    "db_error": (isinstance(WatchdogEntry.exception, exceptions.DbAccessException)), 
                    "rpc_error":(isinstance(WatchdogEntry.exception, exceptions.RpcException)), 
                  } 
        
    return render_to_any_response(HttpResponseServerError, "500.html", context, context_instance=RequestContext(request))

def forbidden(request, user_message):
    """ 
        Permission Denied is handled by custom middleware and re-directed here 
        Django has no native handler for 403, yet... see: http://code.djangoproject.com/ticket/5515
    """ 
    return render_to_any_response(HttpResponseForbidden, "403.html", {"user_message":user_message}, context_instance=RequestContext(request))
