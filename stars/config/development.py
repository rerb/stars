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
        'HOST': 'aashedb',
    }
}

#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_BACKEND = "db://temp_cache_table"

MEDIA_ROOT = '/var/www/stars.dev.aashe.org/media/'

SSO_SERVER_URI = DEV_SSO_SERVER_URI
STARS_DOMAIN = DEV_STARS_DOMAIN
SSO_API_KEY = DEV_SSO_API_KEY

XMLRPC_VERBOSE = False

# Authorize.Net
AUTHORIZENET_LOGIN = TEST_AUTHORIZENET_LOGIN
AUTHORIZENET_KEY = TEST_AUTHORIZENET_KEY
AUTHORIZENET_SERVER = TEST_AUTHORIZENET_SERVER