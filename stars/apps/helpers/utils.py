from django.conf import settings

import sys, re

def settings_context(request):
    """
        This custom template-context processor adds some basic settings
    """
    
    context_dict = {}
    
    settings_list = ['ANALYTICS_ID', 'DEBUG','PYTHON_VERSION', 'DJANGO_VERSION']

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