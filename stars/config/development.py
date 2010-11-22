"""
    This file configures the development environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

DEBUG = True

DATABASES = {
    'default': {
        'NAME': 'stars_dev',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'starsapp',
        'PASSWORD': 'J3z4#$szFET--6',
        'HOST': 'localhost',
    }
}

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

MEDIA_ROOT = '/var/www/stars.dev.aashe.org/media'

SSO_SERVER_URI = DEV_SSO_SERVER_URI
STARS_DOMAIN = DEV_STARS_DOMAIN
SSO_API_KEY = DEV_SSO_API_KEY

XMLRPC_VERBOSE = False

CYBERSOURCE_URL = CYBERSOURCE_TEST_URL
