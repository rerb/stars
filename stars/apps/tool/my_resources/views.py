from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404

from datetime import datetime

from stars.apps.accounts.utils import respond
from stars.apps.accounts.decorators import user_has_tool
from stars.apps.submissions.models import *
from stars.apps.cms.xml_rpc import get_article
from stars.apps.helpers import watchdog

@user_has_tool
def my_resources(request):
    """
        Shows an article from the resource center
    """
    current_inst = request.user.current_inst
    last_rated_submission = current_inst.get_latest_submission()
    
    try:
        node = get_article(4554)
    except Exception, e:
        watchdog.log_exception(e)
    
    if not node:
        watchdog.log('My Resources article not found on IRC', watchdog.ERROR)
        raise Http404
    
    context={
        'node': node,
        'last_submission': last_rated_submission,
        'institution': current_inst,
    }

    return respond(request, "tool/submissions/my_resources.html", context)
