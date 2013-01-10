from django.template import RequestContext
from django.http import HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render_to_response

from stars.apps.helpers.shortcuts import render_to_any_response


class TemplateView(object):
    """
        A generic class view that all other views can extend
    """
    def __init__(self, template):
        self.template = template

    def __call__(self, request, *args, **kwargs):
        """ Simply calls render """

        return self.render(request, *args, **kwargs)

    def render(self, request, *args, **kwargs):
        """ Renders the response """

        context = self.get_context(request, *args, **kwargs)
        if context.__class__.__name__ == "HttpResponseRedirect":
            return context

        return render_to_response(self.template,
                                  context,
                                  context_instance=RequestContext(request))

    def get_context(self, request, *args, **kwargs):
        """ Add/update any context variables """
        _context = {}
        return _context

def server_error(request):
    """Before watchdog moved to a farm upstate where he can run and
    play and chase rabbits all day, the context below was filled with
    info from any exception available via WatchdogEntry.  Not much
    going on here anymore.
    """
    context = {}

    return render_to_any_response(HttpResponseServerError,
                                  "500.html",
                                  context,
                                  context_instance=RequestContext(request))

def forbidden(request, user_message):
    """
        Permission Denied is handled by custom middleware and re-directed here
        Django has no native handler for 403, yet... see: http://code.djangoproject.com/ticket/5515
    """
    return render_to_any_response(HttpResponseForbidden, "403.html", {"user_message":user_message}, context_instance=RequestContext(request))

# THE VIEWS BELOW ARE FOR TESTING / DEBUG / DATA MIGRATION AND SHOULD
# NOT NORMALLY BE INCLUDED IN URLS
def migrate_doc_field_required(request):

    """ Migrate data from the is_required boolean field to the
        required choice field

        Run this script when upgrading from rev. 526 or earlier to
        rev. 528 or later
         - be sure both is_required and required fields are defined in
           DocumentationField model
         - be sure the is_required() method in DocumentationField
           model is NOT defined (comment it out)
         - in DB: alter table credits_documentationfield add required
           varchar(8) def 'req' not null;
         - visit http://your.stars.site/migrate_required
         - in DB: alter table credits_documentationfield drop is_required
         - delete the is_required field from DocumentationField model
    """
    from django.conf import settings
    from django.contrib import messages
    from django.http import HttpResponseRedirect
    from stars.apps.credits.models import DocumentationField

    fields = DocumentationField.objects.all()
    count = 0
    for field in fields:
        if field.is_required:
            field.required = 'req'
        else:
            field.required = 'opt'
        field.save()
        count +=1

    messages.success(request,
                     "Data successfully migrated %s fields from " +
                     "is_required to required field - drop is_required " +
                     "from DB." % count)
    return HttpResponseRedirect(settings.DASHBOARD_URL)

def test(request):
    from stars.apps.accounts.utils import respond
    from stars.apps.tool.credit_editor.forms import NewDocumentationFieldForm
    context = { "form": NewDocumentationFieldForm(),
                "legend": "Context Legend",
                "initial_state": 'collapsed',
               }
    return respond(request, "helpers/test.html", context)
