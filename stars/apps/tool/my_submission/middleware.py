from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from stars.apps.tool.my_submission.views import SubmissionLockedError


class SubmissionLockedErrorMiddleware(object):
    """
    Redirect to a nice "sorry, but that submission is locked" view.
    """
    def process_exception(self, request, exception):
        if isinstance(exception, SubmissionLockedError):
            return HttpResponseRedirect(reverse('submission-locked'))
        return None
