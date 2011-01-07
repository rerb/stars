"""
    This file configures the staging environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'NAME': 'stars_stage',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': 'localhost',
    }
}

MEDIA_ROOT = '/var/www/stars.aashe.org/media'

SSO_SERVER_URI = STAGE_SSO_SERVER_URI
STARS_DOMAIN = STAGE_STARS_DOMAIN
SSO_API_KEY = STAGE_SSO_API_KEY

XMLRPC_VERBOSE = True

CYBERSOURCE_URL = CYBERSOURCE_TEST_URL
