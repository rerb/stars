from django.conf import settings

import sys

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