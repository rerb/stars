import re

from django.conf import settings
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote

def invalidate_template_cache(fragment_name, *variables):
    joined_vars = u':'.join([urlquote(var) for var in variables])
    args = md5_constructor(joined_vars)
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    cache.delete(cache_key)

def settings_context(request):
    """
        This custom template-context processor adds some basic settings
        access these variables in the templates with:

        {{ settings_context.analytics_id }}
    """

    context_dict = {}

    settings_list = ['ANALYTICS_ID', 'DEBUG','PYTHON_VERSION',
                     'DJANGO_VERSION', 'HG_REVISION', 'GOOGLE_MAPS_API_KEY']

    for s in settings_list:
        context_dict[s.lower()] = None
        if hasattr(settings, s):
            context_dict[s.lower()] = getattr(settings, s)

    return {'settings_context': context_dict,}


class StripCookieMiddleware(object):
    """
        Remove Analytics cookies from request before caching middleware gets them
        http://djangosnippets.org/snippets/1772/
        http://code.djangoproject.com/ticket/9249
    """
    strip_re = re.compile(r'(__utm.=.+?(?:; |$))')
    def process_request(self, request):
        try:
            cookie = self.strip_re.sub('', request.META['HTTP_COOKIE'])
            request.META['HTTP_COOKIE'] = cookie
        except: pass
