from django.template import RequestContext

from stars.apps.helpers.shortcuts import render_to_any_response
from stars.apps.auth.maintenancemode.http import HttpResponseTemporaryUnavailable

def temporary_unavailable(request):
    """ 
        Temporarily Unavailable (503) is handled by the maintenance mode middleware and re-directed here 
    """ 
    return render_to_any_response(HttpResponseTemporaryUnavailable, "503.html", {}, context_instance=RequestContext(request))
