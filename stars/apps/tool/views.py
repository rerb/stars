from django.core.exceptions import PermissionDenied

from stars.apps.accounts.utils import respond
from stars.apps.accounts.decorators import user_has_tool
from stars.apps.institutions.rules import user_has_access_level

@user_has_tool
def tool_dashboard(request):
    """
    Display the summary page for the institution
    """
#    if hasattr(request.user, 'current_inst'):
#        current_inst = request.user.current_inst
#    else:
#        raise PermissionDenied("Sorry, but your account does not seem to be associated with an institution.")
#    
#    if not user_has_access_level(request.user, 'preview', request.user.current_inst):
#        raise PermissionDenied("Sorry")
    
    rating_list = request.user.current_inst.submissionset_set.filter(status='r').filter(is_visible=True).order_by('date_submitted')
        
    context = {'current_inst': request.user.current_inst, 'rating_list': rating_list}
    return respond(request, 'tool/tool.html', context)
    
    
