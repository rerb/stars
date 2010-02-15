from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404

from datetime import datetime

from stars.apps.auth.utils import respond
from stars.apps.auth.decorators import user_has_tool
from stars.apps.submissions.models import *
from stars.apps.cms.xml_rpc import get_article
from stars.apps.helpers import watchdog

@user_has_tool
def my_resources(request):
    """
        Shows an article from the resource center
    """
    try:
        node = get_article(4554)
    except Exception, e:
        watchdog.log_exception(e)
    
    if not node:
        watchdog.log('My Resources article not found on IRC', watchdog.ERROR)
        raise Http404
    
    context={
        'node': node,
    }

    return respond(request, "tool/submissions/my_resources.html", context)