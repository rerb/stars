import collections

from django.contrib.auth.decorators import login_required
from django.core import exceptions
from django.core import urlresolvers
from django.http import HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.defaults import page_not_found
from django.views.generic import RedirectView

from stars.apps.helpers.shortcuts import render_to_any_response
from stars.apps.institutions.models import Institution, StarsAccount


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

def new_path_for_old_path(old_path, institution):
    """
    Maps `old_path` (a URL valid in versions prior to 1.2.1) to
    a new URL.  `institution` is required because all these new
    URLs include institution.slug.
    """

    Substitution = collections.namedtuple(typename='Substitution',
                                          field_names=['old', 'new'])

    # A list of substitution transformations:
    substitutions = [Substitution(old='/manage/responsible-parties/',
                                  new='/manage/responsible-party/'),
                     Substitution(old='/manage/users/',
                                  new='/manage/user/'),
                     Substitution(old='/submissions/',
                                  new='/submission/')]

    def insert_institution_slug(path, institution):
        # institution_slug always goes after '/tool/' for now:
        path_components = path.split('/')
        path_components.insert(path_components.index('tool') + 1,
                               institution.slug)
        return '/'.join(path_components)

    def substitute(path):
        """
        Applies substitutions defined above to `path`.
        """
        for substitution in substitutions:
            path = path.replace(substitution.old, substitution.new)
        return path

    path_with_institution_slug = insert_institution_slug(old_path,
                                                         institution)

    path_with_substitutions = substitute(path_with_institution_slug)

    # special cases now:
    if old_path == '/tool/manage/':
        return path_with_substitutions + 'contact/'

    elif old_path == '/tool/submissions/':
        # add the id of the institution's current submission to the path:
        return (path_with_substitutions +
                unicode(institution.current_submission.id) +
                '/')

    else:
        return path_with_substitutions


class OldPathPreserverView(RedirectView):
    """
    Redirects from old URLs (valid in earlier versions) to new,
    valid URLs.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RedirectView, self).dispatch(*args, **kwargs)

    def get_redirect_url(self, **kwargs):
        try:
            stars_account = self.request.user.starsaccount_set.get()
        except exceptions.MultipleObjectsReturned:
            # More than one StarsAccount for this user;
            # redirect to the 'pick an institution, dude' page,
            # passing the requested URL as a GET 'next' parameter:
            return '?'.join([urlresolvers.reverse('select-institution'),
                             'next={path}'.format(path=self.request.path)])
        except StarsAccount.DoesNotExist:
            # User has no StarsAccounts!
            return urlresolvers.reverse('no-stars-account')
        else:
            return new_path_for_old_path(old_path=self.request.path,
                                         institution=stars_account.institution)


def server_error(request):
    """Before watchdog moved to a farm upstate where he can run and
    play and chase rabbits all day, the context below was filled with
    info from any exception available via WatchdogEntry.  Not much
    going on here anymore.
    """
    context = dict()

    return render_to_any_response(HttpResponseServerError,
                                  "500.html",
                                  context,
                                  context_instance=RequestContext(request))


def get_institution_from_path(path):
    """
    Returns the institution specified by the slug in a URL path.
    """
    institution = None
    for part in path.split('/'):
        # Assuming slugs always have dashes in them:
        if '-' in part:
            try:
                institution = Institution.objects.get(slug=part)
            except Institution.DoesNotExist:
                continue
            else:
                break
    return institution


def permission_denied(request):
    """
    Pops the institution derived from the slug in the forbidden URL,
    if there is one, into the template context for 403.html.  Also
    deduces and formats the liaison contact info for that institution,
    then pushes that into the template context, too.
    """

    institution_in_url = get_institution_from_path(request.path)

    # Only show liaison contact info if user has a StarsAccount for this
    # institution:
    liaison_contact_info = ''
    if request.user.starsaccount_set.filter(institution=institution_in_url):
        liaison_phone = institution_in_url.get_liaison_phone()
        liaison_email = institution_in_url.get_liaison_email()
        if liaison_phone or liaison_email:
            liaison_contact_info = '{liaison_name} is available'.format(
                liaison_name=institution_in_url.get_liaison_name())
            if liaison_phone:
                liaison_contact_info += ' by phone at {liaison_phone}'.format(
                    liaison_phone=liaison_phone)
                if liaison_email:
                    liaison_contact_info += ', and'
                else:
                    liaison_contact_info += '.'
            if liaison_email:
                liaison_contact_info += ' via email at {liaison_email}.'.format(
                    liaison_email=liaison_email)

    context = {'institution_in_url': institution_in_url,
               'liaison_contact_info': liaison_contact_info}

    return render_to_any_response(HttpResponseForbidden,
                                  "403.html",
                                  context,
                                  context_instance=RequestContext(request))



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
