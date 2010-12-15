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

CYBERSOURCE_URL = CYBERSOURCE_TEST_URL

GOOGLE_MAPS_API_KEY = "ABQIAAAA-bTvhmGT1R0ug4p1J_-l4hScttncTMtIeIQ67z9yAhEOFftT5RQeXZ-GuqEk2I_f8mwgKudlLLOX_A"
