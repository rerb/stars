from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from stars.apps.auth.utils import respond
from stars.apps.tool.admin.watchdog.models import WatchdogEntry
from stars.apps.tool.admin.watchdog.models import LOG_DURATION
from stars.apps.helpers import flashMessage

"""
    Number of entries for Pagination of log
"""
ENTRIES_PER_PAGE = 25

def list(request):
    """ 
        Summary / List view of recent watchdog log entries, with pager
    """ 
    all_entries = WatchdogEntry.objects.all() #[offset:limit]  for pager
    paginator = Paginator(all_entries, ENTRIES_PER_PAGE) 

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        entries = paginator.page(paginator.num_pages)

    context = {"entries":entries, "expiry_date":_get_log_expiry_date().ctime()}
    template = "tool/admin/watchdog/list.html"
    return respond(request, template, context)  
    
def detail(request, entry_id):
    """
        Detail view of one watchdog entry
    """
    entry = get_object_or_404(WatchdogEntry, id=entry_id)
    context = locals()
    template = "tool/admin/watchdog/detail.html"
    return respond(request, template, context)  
    
def purge(request):
    """
        Purge all expired watchdog log entries - intended to be visited by a cron job
    """
    expiry_date = _get_log_expiry_date()
    entries = WatchdogEntry.objects.all().filter(timestamp__lte=expiry_date)

    num_entries = entries.count()
    entries.delete()

    flashMessage.send("%s entries older than %s were purged from the log."%(num_entries, expiry_date.ctime()), flashMessage.SUCCESS)
    return HttpResponseRedirect(WatchdogEntry.get_admin_url())

def _get_log_expiry_date():
    return datetime.now() - timedelta(**LOG_DURATION)
       
