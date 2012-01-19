from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied

from datetime import datetime

from stars.apps.accounts.utils import respond
from stars.apps.accounts.decorators import user_has_tool
from stars.apps.submissions.models import *
from stars.apps.cms.xml_rpc import get_article
from stars.apps.helpers import watchdog
from stars.apps.institutions.rules import institution_has_my_resources

def my_resources(request):
    """
        Shows an article from the resource center
    """
    if hasattr(request.user, 'current_inst'):
        current_inst = request.user.current_inst
        if not institution_has_my_resources(current_inst):
            raise PermissionDenied("Sorry, only STARS Participants have access to this resource")
    else:
        raise Http404
    
    try:
        node = get_article(4554)
    except Exception, e:
        watchdog.log_exception(e)
    
    if not node:
        watchdog.log('My Resources article not found on IRC', watchdog.ERROR)
        raise Http404
    
    context={
        'node': node,
        'institution': current_inst,
    }

    return respond(request, "tool/submissions/my_resources.html", context)
