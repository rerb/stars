import collections

from django.core import exceptions, urlresolvers
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView

from stars.apps.institutions.models import StarsAccount

# URLs that were valid in 1.2, but replaced in 1.2.1 are
# listed here.  Translation from the old to the new, valid
# paths is done in apps.helpers.views.OldPathPreserverView.
OLD_PATHS_TO_PRESERVE = ['tool/manage/',
                         'tool/manage/migrate/',
                         'tool/manage/payments/',
                         'tool/manage/responsible-parties/',
                         'tool/manage/share-data/',
                         'tool/manage/users/',
                         'tool/submissions/']


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
