from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from stars.apps.institutions.models import Institution
from stars.apps.auth.utils import change_institution
from stars.apps.helpers import watchdog

def select_school(request, institution_id):
    """
        This view updates the session to reflect the selected institution
    """
    if request.user.is_authenticated():
        institution = None
        try:
            institution = Institution.objects.get(id=institution_id)
        except Institution.DoesNotExist:
            watchdog.log('Auth', "Attempt to select non-existent institution id= %s"%institution_id, watchdog.NOTICE)
              
        if change_institution(request, institution):
            return HttpResponseRedirect(settings.DASHBOARD_URL)
        else:
            raise PermissionDenied("Your request could not be completed.")
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)
