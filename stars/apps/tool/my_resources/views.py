from django.http import Http404
from django.core.exceptions import PermissionDenied

from stars.apps.accounts.utils import respond
from stars.apps.institutions.rules import institution_has_my_resources
from stars.apps.cms.models import NewArticle as Article

def my_resources(request):
    """
        Shows an article from the resource center
    """
    if hasattr(request.user, 'current_inst'):
        current_inst = request.user.current_inst
        if not institution_has_my_resources(current_inst):
            raise PermissionDenied("Sorry, only STARS Participants "
                                   "have access to this resource")
    else:
        raise Http404

    node = Article.objects.get(pk=83)

    context={
        'node': node,
        'institution': current_inst,
    }

    return respond(request, "tool/submissions/my_resources.html", context)
