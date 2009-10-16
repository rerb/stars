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

# THE VIEWS BELOW ARE FOR TESTING / DEBUG / DATA MIGRATION AND SHOULD NOT NORMALLY BE INCLUDED IN URLS
def migrate_doc_field_required(request):
    """ Migrate data from the is_required  boolean field to the required choice field 
        Run this script when upgrading from rev. 526 or earlier to rev. 528 or later
         - be sure both is_required and required fields are defined in DocumentationField model
         - in DB:  alter table credits_documentationfield add required varchar(8) def 'req' not null;
         - visit http://your.stars.site/migrate_required
         - in DB: alter table credits_documentationfield drop is_required
         - delete the is_required field from DocumentationField model
    """
    from django.conf import settings
    from django.http import HttpResponseRedirect
    from stars.apps.credits.models import DocumentationField
    from stars.apps.helpers import flashMessage
    
    fields = DocumentationField.objects.all()
    for field in fields:
        field.required = 'req' if field.is_required else 'opt'
        field.save()
    flashMessage.send("Data successfully migrated from is_required to required field - drop is_required from DB.", flashMessage.SUCCESS)
    return HttpResponseRedirect(settings.DASHBOARD_URL)

def test(request):
    from stars.apps.auth.utils import respond
    from stars.apps.dashboard.credit_editor.forms import NewDocumentationFieldForm
    context = { "form": NewDocumentationFieldForm(),
                "legend": "Context Legend",
                "initial_state": 'collapsed',
               }
    return respond(request, "helpers/test.html", context)
