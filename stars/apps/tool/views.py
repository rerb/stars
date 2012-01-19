from django.http import Http404

from stars.apps.accounts.utils import respond
from stars.apps.accounts.decorators import user_has_tool

def tool_dashboard(request):
    """
    Display the summary page for the institution
    """
    if hasattr(request.user, 'current_inst'):
        current_inst = request.user.current_inst
    else:
        raise Http404
    
    rating_list = current_inst.submissionset_set.filter(status='r').filter(is_visible=True).order_by('date_submitted')
        
    context = {'current_inst': current_inst, 'rating_list': rating_list}
    return respond(request, 'tool/tool.html', context)
    
    
